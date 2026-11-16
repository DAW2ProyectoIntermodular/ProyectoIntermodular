"""Conexión a MongoDB (cliente asíncrono de PyMongo)."""
from pymongo import ASCENDING, AsyncMongoClient

from app.core.config import get_ajustes

_cliente: AsyncMongoClient | None = None


def conectar() -> None:
    global _cliente
    _cliente = AsyncMongoClient(get_ajustes().mongodb_uri, tz_aware=True)


async def desconectar() -> None:
    global _cliente
    if _cliente is not None:
        await _cliente.close()
        _cliente = None


def get_db():
    """Dependencia de FastAPI: devuelve la base de datos de la intranet."""
    if _cliente is None:
        raise RuntimeError("La conexión a MongoDB no está inicializada")
    return _cliente[get_ajustes().mongodb_db_name]


async def crear_indices(db) -> None:
    """Índices que garantizan las reglas de unicidad del modelo de datos."""
    await db.usuarios.create_index([("email", ASCENDING)], unique=True)
    await db.usuarios.create_index([("google_id", ASCENDING)], unique=True, sparse=True)
    await db.departamentos.create_index([("codigo", ASCENDING)], unique=True)
