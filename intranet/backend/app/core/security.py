"""Creación y validación de los tokens JWT (access y refresh)."""
import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_ajustes

TIPO_ACCESS = "access"
TIPO_REFRESH = "refresh"


class TokenInvalido(Exception):
    """El token no es válido: firma incorrecta, caducado o de otro tipo."""


def _crear_token(usuario_id: str, tipo: str, duracion: timedelta, extra: dict | None = None) -> str:
    ajustes = get_ajustes()
    ahora = datetime.now(timezone.utc)
    datos = {
        "sub": usuario_id,
        "tipo": tipo,
        "jti": uuid.uuid4().hex,
        "iat": ahora,
        "exp": ahora + duracion,
        **(extra or {}),
    }
    return jwt.encode(datos, ajustes.jwt_secret_key, algorithm=ajustes.jwt_algorithm)


def crear_access_token(usuario_id: str, email: str, roles: list[str]) -> str:
    minutos = get_ajustes().jwt_access_token_expire_minutes
    return _crear_token(usuario_id, TIPO_ACCESS, timedelta(minutes=minutos), {"email": email, "roles": roles})


def crear_refresh_token(usuario_id: str) -> str:
    dias = get_ajustes().jwt_refresh_token_expire_days
    return _crear_token(usuario_id, TIPO_REFRESH, timedelta(days=dias))


def decodificar_token(token: str, tipo_esperado: str) -> dict:
    """Devuelve el contenido del token o lanza TokenInvalido."""
    ajustes = get_ajustes()
    try:
        datos = jwt.decode(token, ajustes.jwt_secret_key, algorithms=[ajustes.jwt_algorithm])
    except jwt.PyJWTError as error:
        raise TokenInvalido(str(error)) from error
    if datos.get("tipo") != tipo_esperado or "sub" not in datos or "jti" not in datos:
        raise TokenInvalido("Tipo de token incorrecto")
    return datos
