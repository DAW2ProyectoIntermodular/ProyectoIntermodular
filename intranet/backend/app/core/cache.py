"""Conexión a Redis. En la Fase 1 se usa para revocar refresh tokens."""
from redis.asyncio import Redis

from app.core.config import get_ajustes

_redis: Redis | None = None


def conectar() -> None:
    global _redis
    _redis = Redis.from_url(get_ajustes().redis_url, decode_responses=True)


async def desconectar() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None


def get_redis() -> Redis:
    """Dependencia de FastAPI: devuelve el cliente de Redis."""
    if _redis is None:
        raise RuntimeError("La conexión a Redis no está inicializada")
    return _redis
