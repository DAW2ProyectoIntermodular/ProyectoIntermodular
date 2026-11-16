"""Dependencias de autenticación y control de roles para los endpoints."""
from typing import Annotated

from bson import ObjectId
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.database import get_db
from app.core.errores import AccesoDenegado, NoAutenticado
from app.core.security import TIPO_ACCESS, TokenInvalido, decodificar_token
from app.models.usuario import EstadoUsuario, Rol

# auto_error=False para responder nosotros con 401 y el formato {"detail": ...}
esquema_bearer = HTTPBearer(auto_error=False, description="Access token JWT")

MENSAJE_401 = "Token de autenticación ausente o inválido."
MENSAJE_403 = "No dispone de los permisos necesarios para realizar esta acción."


async def get_usuario_actual(
    credenciales: Annotated[HTTPAuthorizationCredentials | None, Depends(esquema_bearer)],
    db=Depends(get_db),
) -> dict:
    """Devuelve el documento del usuario autenticado o lanza 401.

    El usuario se lee de la base de datos en cada petición: así un cambio de roles
    o una desactivación tienen efecto inmediato, sin esperar a que caduque el token.
    """
    if credenciales is None:
        raise NoAutenticado(MENSAJE_401)
    try:
        datos = decodificar_token(credenciales.credentials, TIPO_ACCESS)
    except TokenInvalido:
        raise NoAutenticado(MENSAJE_401)

    usuario = await db.usuarios.find_one({"_id": ObjectId(datos["sub"])})
    if usuario is None or usuario["estado"] != EstadoUsuario.ACTIVO:
        raise NoAutenticado(MENSAJE_401)
    return usuario


UsuarioActual = Annotated[dict, Depends(get_usuario_actual)]


def requiere_roles(*roles_permitidos: Rol):
    """Crea una dependencia que exige al menos uno de los roles indicados.

    Uso: `admin: dict = Depends(requiere_roles(Rol.ADMINISTRADOR))`
    El rol `administrador` tiene acceso total, así que siempre pasa.
    """
    permitidos = set(roles_permitidos) | {Rol.ADMINISTRADOR}

    async def comprobar(usuario: UsuarioActual) -> dict:
        if not permitidos.intersection(usuario["roles"]):
            raise AccesoDenegado(MENSAJE_403)
        return usuario

    return comprobar
