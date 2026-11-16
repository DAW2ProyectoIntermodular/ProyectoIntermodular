"""Esquemas de autenticación (según el contrato OpenAPI)."""
from pydantic import BaseModel, EmailStr

from app.schemas.usuario import Usuario


class LoginGoogleRequest(BaseModel):
    credential: str


class LoginDesarrolloRequest(BaseModel):
    email: EmailStr


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenPar(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginRespuesta(BaseModel):
    tokens: TokenPar
    usuario: Usuario
