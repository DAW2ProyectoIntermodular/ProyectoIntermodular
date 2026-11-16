"""Lógica de departamentos didácticos."""
from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.core.errores import Conflicto, DatoNoValido, NoEncontrado
from app.schemas.departamento import Departamento, DepartamentoCrear


async def nombres_por_id(db, ids) -> dict[ObjectId, str]:
    """Devuelve {id: nombre} de los departamentos indicados (una sola consulta)."""
    ids = [i for i in set(ids) if i is not None]
    if not ids:
        return {}
    cursor = db.departamentos.find({"_id": {"$in": ids}}, {"nombre": 1})
    return {doc["_id"]: doc["nombre"] async for doc in cursor}


async def existe(db, departamento_id: str) -> bool:
    return await db.departamentos.count_documents({"_id": ObjectId(departamento_id)}) > 0


async def _a_esquema(db, doc: dict) -> Departamento:
    jefe_nombre = None
    if doc.get("jefe_departamento_id"):
        jefe = await db.usuarios.find_one({"_id": doc["jefe_departamento_id"]}, {"nombre": 1, "apellidos": 1})
        if jefe:
            jefe_nombre = f'{jefe["nombre"]} {jefe["apellidos"]}'
    return Departamento(
        id=str(doc["_id"]),
        codigo=doc["codigo"],
        nombre=doc["nombre"],
        descripcion=doc.get("descripcion", ""),
        jefe_departamento_id=str(doc["jefe_departamento_id"]) if doc.get("jefe_departamento_id") else None,
        jefe_departamento_nombre=jefe_nombre,
        miembros_count=await db.usuarios.count_documents({"departamento_id": doc["_id"]}),
    )


async def _documento_desde(db, datos: DepartamentoCrear) -> dict:
    jefe_id = None
    if datos.jefe_departamento_id:
        jefe_id = ObjectId(datos.jefe_departamento_id)
        if await db.usuarios.count_documents({"_id": jefe_id}) == 0:
            raise DatoNoValido("jefe_departamento_id", "El usuario indicado como jefe de departamento no existe")
    return {
        "codigo": datos.codigo.strip().upper(),
        "nombre": datos.nombre.strip(),
        "descripcion": datos.descripcion,
        "jefe_departamento_id": jefe_id,
    }


async def listar(db, page: int, limit: int) -> tuple[list[Departamento], int]:
    total = await db.departamentos.count_documents({})
    cursor = db.departamentos.find({}).sort("nombre", 1).skip((page - 1) * limit).limit(limit)
    items = [await _a_esquema(db, doc) async for doc in cursor]
    return items, total


async def obtener(db, departamento_id: str) -> Departamento:
    doc = await db.departamentos.find_one({"_id": ObjectId(departamento_id)})
    if doc is None:
        raise NoEncontrado("El departamento solicitado no existe.")
    return await _a_esquema(db, doc)


async def crear(db, datos: DepartamentoCrear) -> Departamento:
    doc = await _documento_desde(db, datos)
    try:
        resultado = await db.departamentos.insert_one(doc)
    except DuplicateKeyError:
        raise Conflicto("Ya existe un departamento con ese código.")
    doc["_id"] = resultado.inserted_id
    return await _a_esquema(db, doc)


async def actualizar(db, departamento_id: str, datos: DepartamentoCrear) -> Departamento:
    cambios = await _documento_desde(db, datos)
    try:
        doc = await db.departamentos.find_one_and_update(
            {"_id": ObjectId(departamento_id)}, {"$set": cambios}, return_document=ReturnDocument.AFTER
        )
    except DuplicateKeyError:
        raise Conflicto("Ya existe un departamento con ese código.")
    if doc is None:
        raise NoEncontrado("El departamento solicitado no existe.")
    return await _a_esquema(db, doc)
