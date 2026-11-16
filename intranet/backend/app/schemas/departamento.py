"""Esquemas de departamentos (según el contrato OpenAPI)."""
from pydantic import BaseModel, Field

from app.schemas.comun import PATRON_OBJECT_ID


class Departamento(BaseModel):
    id: str
    codigo: str
    nombre: str
    descripcion: str = ""
    jefe_departamento_id: str | None = None
    jefe_departamento_nombre: str | None = None
    miembros_count: int = 0


class DepartamentoCrear(BaseModel):
    codigo: str = Field(min_length=1)
    nombre: str = Field(min_length=1)
    descripcion: str = ""
    jefe_departamento_id: str | None = Field(default=None, pattern=PATRON_OBJECT_ID)
