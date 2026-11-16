"""Verificación del token de identidad que entrega Google al iniciar sesión."""
from dataclasses import dataclass

from fastapi.concurrency import run_in_threadpool
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.core.config import get_ajustes
from app.core.errores import NoAutenticado


@dataclass
class DatosGoogle:
    google_id: str
    email: str
    nombre: str
    apellidos: str
    foto_url: str | None


async def verificar_credencial_google(credential: str) -> DatosGoogle:
    """Comprueba con Google que el token es auténtico y va dirigido a nuestra aplicación."""
    client_id = get_ajustes().google_client_id
    if not client_id:
        raise NoAutenticado("El inicio de sesión con Google no está configurado (falta GOOGLE_CLIENT_ID).")
    try:
        # La librería es síncrona y hace una petición de red: se ejecuta en un hilo aparte.
        datos = await run_in_threadpool(
            id_token.verify_oauth2_token, credential, google_requests.Request(), client_id
        )
    except Exception:
        raise NoAutenticado("La credencial de Google no es válida o ha caducado.")
    if not datos.get("email") or not datos.get("email_verified"):
        raise NoAutenticado("La cuenta de Google no tiene un correo verificado.")
    return DatosGoogle(
        google_id=datos["sub"],
        email=datos["email"],
        nombre=datos.get("given_name") or datos["email"].split("@")[0],
        apellidos=datos.get("family_name") or "",
        foto_url=datos.get("picture"),
    )


def get_verificador_google():
    """Dependencia de FastAPI. Los tests la sustituyen por un verificador falso."""
    return verificar_credencial_google
