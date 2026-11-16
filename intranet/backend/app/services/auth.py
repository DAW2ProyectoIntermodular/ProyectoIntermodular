"""Lógica de autenticación: login, renovación y cierre de sesión."""
import time

from bson import ObjectId

from app.core.config import get_ajustes
from app.core.errores import AccesoDenegado, NoAutenticado
from app.core.security import (
    TIPO_REFRESH,
    TokenInvalido,
    crear_access_token,
    crear_refresh_token,
    decodificar_token,
)
from app.models.usuario import EstadoUsuario, Rol
from app.schemas.auth import TokenPar
from app.services import usuarios as servicio_usuarios
from app.services.google import DatosGoogle

MENSAJE_REFRESH_INVALIDO = "Refresh token inválido, revocado o expirado."
MENSAJE_PENDIENTE = "Tu cuenta está pendiente de confirmación por un administrador."
MENSAJE_INACTIVO = "Tu cuenta está desactivada. Contacta con un administrador."


def emitir_tokens(usuario: dict) -> TokenPar:
    usuario_id = str(usuario["_id"])
    return TokenPar(
        access_token=crear_access_token(usuario_id, usuario["email"], usuario["roles"]),
        refresh_token=crear_refresh_token(usuario_id),
        expires_in=get_ajustes().jwt_access_token_expire_minutes * 60,
    )


def _exigir_activo(usuario: dict) -> None:
    if usuario["estado"] == EstadoUsuario.PENDIENTE:
        raise AccesoDenegado(MENSAJE_PENDIENTE)
    if usuario["estado"] != EstadoUsuario.ACTIVO:
        raise AccesoDenegado(MENSAJE_INACTIVO)


async def _registrar_acceso(db, usuario: dict, cambios: dict | None = None) -> dict:
    cambios = {**(cambios or {}), "ultimo_acceso": servicio_usuarios.ahora()}
    await db.usuarios.update_one({"_id": usuario["_id"]}, {"$set": cambios})
    return {**usuario, **cambios}


async def login_google(db, datos: DatosGoogle) -> dict:
    """Devuelve el usuario si puede entrar. Casos:

    1. Ya entró antes con esa cuenta de Google -> se busca por google_id.
    2. Un administrador lo dio de alta a mano -> se busca por correo y se vincula su Google.
    3. No existe -> se registra como "pendiente_confirmacion" y se responde 403.
    """
    usuario = await db.usuarios.find_one({"google_id": datos.google_id})
    cambios = {}
    if usuario is None:
        usuario = await db.usuarios.find_one({"email": datos.email.lower()})
        if usuario is not None:
            cambios["google_id"] = datos.google_id
            if not usuario.get("foto_url"):
                cambios["foto_url"] = datos.foto_url

    if usuario is None:
        await db.usuarios.insert_one(
            servicio_usuarios.nuevo_documento(
                email=datos.email,
                nombre=datos.nombre,
                apellidos=datos.apellidos,
                foto_url=datos.foto_url,
                google_id=datos.google_id,
                roles=[Rol.PROFESOR],
                estado=EstadoUsuario.PENDIENTE,
            )
        )
        raise AccesoDenegado(MENSAJE_PENDIENTE)

    _exigir_activo(usuario)
    return await _registrar_acceso(db, usuario, cambios)


async def login_desarrollo(db, email: str) -> dict:
    """Entrada sin Google para un usuario que ya existe. Solo en entorno de desarrollo."""
    usuario = await db.usuarios.find_one({"email": email.lower()})
    if usuario is None:
        raise NoAutenticado("No existe ningún usuario con ese correo.")
    _exigir_activo(usuario)
    return await _registrar_acceso(db, usuario)


def _clave_revocado(jti: str) -> str:
    return f"refresh_revocado:{jti}"


async def _revocar(redis, datos_token: dict) -> None:
    """Apunta el token en Redis hasta el momento en que habría caducado por sí solo."""
    segundos_restantes = int(datos_token["exp"] - time.time())
    if segundos_restantes > 0:
        await redis.set(_clave_revocado(datos_token["jti"]), "1", ex=segundos_restantes)


async def renovar(db, redis, refresh_token: str) -> TokenPar:
    """Cambia un refresh token válido por un par nuevo (rotación).

    El refresh token usado se revoca: cada uno sirve una sola vez.
    """
    try:
        datos = decodificar_token(refresh_token, TIPO_REFRESH)
    except TokenInvalido:
        raise NoAutenticado(MENSAJE_REFRESH_INVALIDO)
    if await redis.exists(_clave_revocado(datos["jti"])):
        raise NoAutenticado(MENSAJE_REFRESH_INVALIDO)

    usuario = await db.usuarios.find_one({"_id": ObjectId(datos["sub"])})
    if usuario is None or usuario["estado"] != EstadoUsuario.ACTIVO:
        raise NoAutenticado(MENSAJE_REFRESH_INVALIDO)

    await _revocar(redis, datos)
    return emitir_tokens(usuario)


async def cerrar_sesion(redis, usuario: dict, refresh_token: str) -> None:
    """Revoca el refresh token del usuario. Si el token no es válido no hay nada que revocar."""
    try:
        datos = decodificar_token(refresh_token, TIPO_REFRESH)
    except TokenInvalido:
        return
    if datos["sub"] == str(usuario["_id"]):
        await _revocar(redis, datos)
