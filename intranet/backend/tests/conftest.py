"""Preparación común de los tests.

No hace falta MongoDB ni Redis reales: se sustituyen por versiones en memoria
(mongomock y fakeredis) usando las dependencias de FastAPI.
"""
import pytest
from fakeredis import FakeAsyncRedis
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.core.cache import get_redis
from app.core.database import crear_indices, get_db
from app.core.errores import NoAutenticado
from app.main import app
from app.models.usuario import EstadoUsuario, Rol
from app.services import auth as servicio_auth
from app.services import usuarios as servicio_usuarios
from app.services.google import DatosGoogle, get_verificador_google


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def db():
    base = AsyncMongoMockClient(tz_aware=True)["intranet_test"]
    await crear_indices(base)
    return base


@pytest.fixture
async def redis():
    return FakeAsyncRedis(decode_responses=True)


async def verificador_google_falso(credential: str) -> DatosGoogle:
    """Simula a Google: la credencial "google:<correo>" es válida; cualquier otra, no."""
    if not credential.startswith("google:"):
        raise NoAutenticado("La credencial de Google no es válida o ha caducado.")
    email = credential.removeprefix("google:")
    return DatosGoogle(
        google_id=f"gid-{email}", email=email, nombre="Nombre", apellidos="Google", foto_url=None
    )


@pytest.fixture
async def cliente(db, redis):
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_redis] = lambda: redis
    app.dependency_overrides[get_verificador_google] = lambda: verificador_google_falso
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def crear_usuario(db):
    """Inserta un usuario directamente en la base de datos y lo devuelve."""

    async def _crear(email="profe@example.org", roles=(Rol.PROFESOR,), estado=EstadoUsuario.ACTIVO, **extra):
        doc = servicio_usuarios.nuevo_documento(
            email=email, nombre="Nombre", apellidos="Apellidos", roles=list(roles), estado=estado, **extra
        )
        doc["_id"] = (await db.usuarios.insert_one(doc)).inserted_id
        return doc

    return _crear


def cabeceras(usuario: dict) -> dict:
    """Cabecera Authorization con un access token válido para ese usuario."""
    return {"Authorization": f"Bearer {servicio_auth.emitir_tokens(usuario).access_token}"}


@pytest.fixture
async def admin(crear_usuario):
    return await crear_usuario("admin@example.org", roles=(Rol.ADMINISTRADOR,))


@pytest.fixture
async def profesor(crear_usuario):
    return await crear_usuario("profe@example.org")


@pytest.fixture
async def departamento(db):
    doc = {"codigo": "DEP-INF", "nombre": "Informática", "descripcion": "", "jefe_departamento_id": None}
    doc["_id"] = (await db.departamentos.insert_one(doc)).inserted_id
    return doc
