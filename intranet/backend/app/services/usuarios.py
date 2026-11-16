"""Lógica de usuarios: altas, consultas, estados y roles."""
import re
from datetime import datetime, timezone

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.core.errores import Conflicto, DatoNoValido, NoEncontrado
from app.models.usuario import TRANSICIONES_ESTADO, EstadoUsuario, Rol
from app.schemas.usuario import (
    Usuario,
    UsuarioActualizar,
    UsuarioCrear,
    UsuarioEstadoPatch,
    UsuarioPerfilActualizar,
)
from app.services import departamentos as servicio_departamentos

MENSAJE_NO_ENCONTRADO = "El usuario solicitado no existe."
MENSAJE_EMAIL_DUPLICADO = "El correo electrónico ya está registrado en el sistema."


def ahora() -> datetime:
    """Fecha actual en UTC con precisión de milisegundos, que es la que guarda MongoDB."""
    momento = datetime.now(timezone.utc)
    return momento.replace(microsecond=momento.microsecond // 1000 * 1000)


def nuevo_documento(
    *,
    email: str,
    nombre: str,
    apellidos: str,
    roles: list[str],
    estado: str,
    telefono: str | None = None,
    foto_url: str | None = None,
    departamento_id: ObjectId | None = None,
    google_id: str | None = None,
) -> dict:
    """Documento de la colección `usuarios` con todos sus campos."""
    doc = {
        "email": email.lower(),
        "nombre": nombre,
        "apellidos": apellidos,
        "telefono": telefono,
        "foto_url": foto_url,
        "biografia": None,
        "departamento_id": departamento_id,
        "roles": [str(rol) for rol in roles],
        "estado": str(estado),
        "fecha_creacion": ahora(),
        "ultimo_acceso": None,
    }
    # google_id solo se guarda cuando existe: el índice único es "sparse".
    if google_id:
        doc["google_id"] = google_id
    return doc


def a_esquema(doc: dict, nombres_departamento: dict | None = None) -> Usuario:
    departamento_id = doc.get("departamento_id")
    return Usuario(
        id=str(doc["_id"]),
        email=doc["email"],
        nombre=doc["nombre"],
        apellidos=doc["apellidos"],
        telefono=doc.get("telefono"),
        foto_url=doc.get("foto_url"),
        biografia=doc.get("biografia"),
        departamento_id=str(departamento_id) if departamento_id else None,
        departamento_nombre=(nombres_departamento or {}).get(departamento_id),
        roles=doc["roles"],
        estado=doc["estado"],
        google_id=doc.get("google_id"),
        fecha_creacion=doc["fecha_creacion"],
        ultimo_acceso=doc.get("ultimo_acceso"),
    )


async def a_esquema_completo(db, doc: dict) -> Usuario:
    """Igual que a_esquema, pero buscando el nombre del departamento."""
    nombres = await servicio_departamentos.nombres_por_id(db, [doc.get("departamento_id")])
    return a_esquema(doc, nombres)


async def _obtener_doc(db, usuario_id: str) -> dict:
    doc = await db.usuarios.find_one({"_id": ObjectId(usuario_id)})
    if doc is None:
        raise NoEncontrado(MENSAJE_NO_ENCONTRADO)
    return doc


async def _comprobar_departamento(db, departamento_id: str) -> ObjectId:
    if not await servicio_departamentos.existe(db, departamento_id):
        raise DatoNoValido("departamento_id", "El departamento indicado no existe")
    return ObjectId(departamento_id)


def _comprobar_transicion(estado_actual: str, estado_nuevo: str) -> None:
    if estado_nuevo not in TRANSICIONES_ESTADO[EstadoUsuario(estado_actual)]:
        raise Conflicto(f"Transición de estado inválida: de '{estado_actual}' a '{estado_nuevo}'.")


def _impedir_autobloqueo(usuario_id: str, admin: dict, accion: str) -> None:
    """Un administrador no puede desactivarse, borrarse ni quitarse el rol a sí mismo:
    así el sistema nunca se queda sin nadie que pueda administrarlo por un despiste."""
    if ObjectId(usuario_id) == admin["_id"]:
        raise Conflicto(f"No puedes {accion} tu propia cuenta de administrador.")


async def listar(
    db,
    *,
    page: int,
    limit: int,
    estado: EstadoUsuario | None = None,
    rol: Rol | None = None,
    departamento_id: str | None = None,
    busqueda: str | None = None,
) -> tuple[list[Usuario], int]:
    filtro: dict = {}
    if estado:
        filtro["estado"] = str(estado)
    if rol:
        filtro["roles"] = str(rol)
    if departamento_id:
        filtro["departamento_id"] = ObjectId(departamento_id)
    if busqueda:
        # re.escape evita que el texto del usuario se interprete como expresión regular
        patron = {"$regex": re.escape(busqueda.strip()), "$options": "i"}
        filtro["$or"] = [{"nombre": patron}, {"apellidos": patron}, {"email": patron}]

    total = await db.usuarios.count_documents(filtro)
    cursor = db.usuarios.find(filtro).sort([("apellidos", 1), ("nombre", 1)]).skip((page - 1) * limit).limit(limit)
    docs = await cursor.to_list(length=limit)
    nombres = await servicio_departamentos.nombres_por_id(db, [d.get("departamento_id") for d in docs])
    return [a_esquema(doc, nombres) for doc in docs], total


async def obtener(db, usuario_id: str) -> Usuario:
    return await a_esquema_completo(db, await _obtener_doc(db, usuario_id))


async def crear(db, datos: UsuarioCrear) -> Usuario:
    """Alta manual por un administrador (sin necesidad de login previo con Google)."""
    doc = nuevo_documento(
        email=datos.email,
        nombre=datos.nombre.strip(),
        apellidos=datos.apellidos.strip(),
        telefono=datos.telefono,
        departamento_id=await _comprobar_departamento(db, datos.departamento_id),
        roles=datos.roles,
        estado=datos.estado,
    )
    try:
        resultado = await db.usuarios.insert_one(doc)
    except DuplicateKeyError:
        raise Conflicto(MENSAJE_EMAIL_DUPLICADO)
    doc["_id"] = resultado.inserted_id
    return await a_esquema_completo(db, doc)


async def reemplazar(db, usuario_id: str, datos: UsuarioActualizar, admin: dict) -> Usuario:
    actual = await _obtener_doc(db, usuario_id)
    if datos.estado != actual["estado"]:
        _impedir_autobloqueo(usuario_id, admin, "cambiar el estado de")
        _comprobar_transicion(actual["estado"], datos.estado)
    if Rol.ADMINISTRADOR not in datos.roles:
        _impedir_autobloqueo(usuario_id, admin, "quitar el rol de administrador a")

    cambios = {
        "email": datos.email.lower(),
        "nombre": datos.nombre.strip(),
        "apellidos": datos.apellidos.strip(),
        "telefono": datos.telefono,
        "departamento_id": await _comprobar_departamento(db, datos.departamento_id),
        "roles": [str(rol) for rol in datos.roles],
        "estado": str(datos.estado),
    }
    try:
        doc = await db.usuarios.find_one_and_update(
            {"_id": actual["_id"]}, {"$set": cambios}, return_document=ReturnDocument.AFTER
        )
    except DuplicateKeyError:
        raise Conflicto(MENSAJE_EMAIL_DUPLICADO)
    return await a_esquema_completo(db, doc)


async def cambiar_estado(db, usuario_id: str, datos: UsuarioEstadoPatch, admin: dict) -> Usuario:
    """Aprueba un alta pendiente, o activa/desactiva una cuenta."""
    _impedir_autobloqueo(usuario_id, admin, "cambiar el estado de")
    actual = await _obtener_doc(db, usuario_id)
    _comprobar_transicion(actual["estado"], datos.estado)
    doc = await db.usuarios.find_one_and_update(
        {"_id": actual["_id"]}, {"$set": {"estado": str(datos.estado)}}, return_document=ReturnDocument.AFTER
    )
    return await a_esquema_completo(db, doc)


async def cambiar_roles(db, usuario_id: str, roles: list[Rol], admin: dict) -> Usuario:
    if Rol.ADMINISTRADOR not in roles:
        _impedir_autobloqueo(usuario_id, admin, "quitar el rol de administrador a")
    sin_repetidos = list(dict.fromkeys(str(rol) for rol in roles))
    doc = await db.usuarios.find_one_and_update(
        {"_id": ObjectId(usuario_id)}, {"$set": {"roles": sin_repetidos}}, return_document=ReturnDocument.AFTER
    )
    if doc is None:
        raise NoEncontrado(MENSAJE_NO_ENCONTRADO)
    return await a_esquema_completo(db, doc)


async def eliminar(db, usuario_id: str, admin: dict) -> None:
    _impedir_autobloqueo(usuario_id, admin, "eliminar")
    resultado = await db.usuarios.delete_one({"_id": ObjectId(usuario_id)})
    if resultado.deleted_count == 0:
        raise NoEncontrado(MENSAJE_NO_ENCONTRADO)


async def actualizar_perfil(db, usuario: dict, datos: UsuarioPerfilActualizar) -> Usuario:
    """El propio usuario cambia sus datos de contacto. Solo se tocan los campos enviados."""
    cambios = datos.model_dump(exclude_unset=True)
    doc = usuario
    if cambios:
        doc = await db.usuarios.find_one_and_update(
            {"_id": usuario["_id"]}, {"$set": cambios}, return_document=ReturnDocument.AFTER
        )
    return await a_esquema_completo(db, doc)


async def crear_primer_administrador(db, email: str) -> bool:
    """Crea el administrador inicial si todavía no existe un usuario con ese correo.

    Hace falta porque las altas las aprueba un administrador: sin este primer
    usuario nadie podría entrar. Al iniciar sesión con Google con ese mismo correo,
    la cuenta de Google queda vinculada.
    """
    if await db.usuarios.count_documents({"email": email.lower()}) > 0:
        return False
    await db.usuarios.insert_one(
        nuevo_documento(
            email=email,
            nombre="Administrador",
            apellidos="Inicial",
            roles=[Rol.ADMINISTRADOR, Rol.PROFESOR],
            estado=EstadoUsuario.ACTIVO,
        )
    )
    return True
