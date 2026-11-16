"""Endpoints de autenticación."""
from fastapi import APIRouter, Depends, status

from app.core.cache import get_redis
from app.core.config import get_ajustes
from app.core.database import get_db
from app.core.permisos import UsuarioActual
from app.schemas.auth import (
    LoginDesarrolloRequest,
    LoginGoogleRequest,
    LoginRespuesta,
    RefreshTokenRequest,
    TokenPar,
)
from app.services import auth as servicio_auth
from app.services import usuarios as servicio_usuarios
from app.services.google import get_verificador_google

router = APIRouter(prefix="/auth", tags=["Autenticación"])


async def _respuesta_login(db, usuario: dict) -> LoginRespuesta:
    return LoginRespuesta(
        tokens=servicio_auth.emitir_tokens(usuario),
        usuario=await servicio_usuarios.a_esquema_completo(db, usuario),
    )


@router.post("/login/google", response_model=LoginRespuesta, summary="Iniciar sesión con Google OAuth2")
async def login_google(
    cuerpo: LoginGoogleRequest,
    db=Depends(get_db),
    verificar=Depends(get_verificador_google),
):
    datos_google = await verificar(cuerpo.credential)
    usuario = await servicio_auth.login_google(db, datos_google)
    return await _respuesta_login(db, usuario)


@router.post("/refresh", response_model=TokenPar, summary="Renovar token de acceso JWT")
async def renovar_token(cuerpo: RefreshTokenRequest, db=Depends(get_db), redis=Depends(get_redis)):
    return await servicio_auth.renovar(db, redis, cuerpo.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Cerrar sesión e invalidar tokens")
async def cerrar_sesion(cuerpo: RefreshTokenRequest, usuario: UsuarioActual, redis=Depends(get_redis)):
    await servicio_auth.cerrar_sesion(redis, usuario, cuerpo.refresh_token)


# Atajo para desarrollar sin configurar Google. La ruta ni siquiera existe
# cuando ENVIRONMENT no es "development".
if get_ajustes().es_desarrollo:

    @router.post(
        "/login/dev",
        response_model=LoginRespuesta,
        summary="[Solo desarrollo] Iniciar sesión con el correo de un usuario existente",
    )
    async def login_desarrollo(cuerpo: LoginDesarrolloRequest, db=Depends(get_db)):
        usuario = await servicio_auth.login_desarrollo(db, cuerpo.email)
        return await _respuesta_login(db, usuario)
