"""Configuración de la aplicación, leída de variables de entorno (.env)."""
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

CLAVE_SOLO_DESARROLLO = "clave-solo-para-desarrollo-local-no-usar-en-produccion"


class Ajustes(BaseSettings):
    # Se busca el .env en la carpeta del backend y en la raíz del repositorio.
    model_config = SettingsConfigDict(env_file=(".env", "../../.env"), extra="ignore")

    environment: str = "development"
    cors_origins: str = "http://localhost:5173"

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "intranet"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    google_client_id: str = ""

    # Correo del primer administrador. Si se indica y no existe, se crea al arrancar.
    primer_admin_email: str = ""

    @property
    def es_desarrollo(self) -> bool:
        return self.environment == "development"

    @property
    def lista_cors(self) -> list[str]:
        return [origen.strip() for origen in self.cors_origins.split(",") if origen.strip()]

    @model_validator(mode="after")
    def comprobar_clave_jwt(self):
        if not self.jwt_secret_key:
            if not self.es_desarrollo:
                raise ValueError("JWT_SECRET_KEY es obligatoria fuera del entorno de desarrollo")
            self.jwt_secret_key = CLAVE_SOLO_DESARROLLO
        return self


@lru_cache
def get_ajustes() -> Ajustes:
    return Ajustes()
