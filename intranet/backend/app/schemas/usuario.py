"""Esquemas de entrada y salida de usuarios (según el contrato OpenAPI)."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.usuario import EstadoUsuario, Rol
from app.schemas.comun import PATRON_OBJECT_ID


class Usuario(BaseModel):
    id: str
    email: EmailStr
    nombre: str
    apellidos: str
    telefono: str | None = None
    foto_url: str | None = None
    biografia: str | None = None
    departamento_id: str | None = None
    departamento_nombre: str | None = None
    roles: list[Rol]
    estado: EstadoUsuario
    google_id: str | None = None
    fecha_creacion: datetime
    ultimo_acceso: datetime | None = None


class UsuarioCrear(BaseModel):
    email: EmailStr
    nombre: str = Field(min_length=1)
    apellidos: str = Field(min_length=1)
    telefono: str | None = None
    departamento_id: str = Field(pattern=PATRON_OBJECT_ID)
    roles: list[Rol] = Field(default=[Rol.PROFESOR], min_length=1)
    estado: EstadoUsuario = EstadoUsuario.ACTIVO


class UsuarioActualizar(BaseModel):
    email: EmailStr
    nombre: str = Field(min_length=1)
    apellidos: str = Field(min_length=1)
    telefono: str | None = None
    departamento_id: str = Field(pattern=PATRON_OBJECT_ID)
    roles: list[Rol] = Field(min_length=1)
    estado: EstadoUsuario


class UsuarioPerfilActualizar(BaseModel):
    telefono: str | None = None
    foto_url: str | None = None
    biografia: str | None = None


class UsuarioEstadoPatch(BaseModel):
    estado: EstadoUsuario
    motivo: str | None = None


class UsuarioRolesPut(BaseModel):
    roles: list[Rol] = Field(min_length=1)
