"""Esquemas compartidos por varios módulos."""
from typing import Annotated, Generic, TypeVar

from fastapi import Path, Query
from pydantic import BaseModel

T = TypeVar("T")

PATRON_OBJECT_ID = r"^[0-9a-fA-F]{24}$"

# Identificador de MongoDB recibido en la ruta. Si no tiene el formato correcto -> 422.
IdRuta = Annotated[str, Path(pattern=PATRON_OBJECT_ID)]

# Parámetros de paginación comunes a todos los listados.
Pagina_ = Annotated[int, Query(ge=1, description="Número de página (empieza en 1)")]
Limite_ = Annotated[int, Query(ge=1, le=50, description="Elementos por página (máximo 50)")]


class Pagina(BaseModel, Generic[T]):
    """Respuesta paginada estándar: {"items": [...], "page": 1, "limit": 10, "total": N}."""

    items: list[T]
    page: int
    limit: int
    total: int
