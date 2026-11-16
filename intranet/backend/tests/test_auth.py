"""Tests de autenticación: login con Google, tokens, renovación y cierre de sesión."""
from datetime import timedelta

import pytest

from app.core import security
from app.models.usuario import EstadoUsuario
from app.services import auth as servicio_auth
from tests.conftest import cabeceras

pytestmark = pytest.mark.anyio

LOGIN = "/api/v1/auth/login/google"
REFRESH = "/api/v1/auth/refresh"
LOGOUT = "/api/v1/auth/logout"
ME = "/api/v1/usuarios/me"


async def test_login_usuario_nuevo_queda_pendiente_y_responde_403(cliente, db):
    r = await cliente.post(LOGIN, json={"credential": "google:nuevo@example.org"})

    assert r.status_code == 403
    usuario = await db.usuarios.find_one({"email": "nuevo@example.org"})
    assert usuario["estado"] == EstadoUsuario.PENDIENTE
    assert usuario["roles"] == ["profesor"]

    # Si lo intenta otra vez sigue pendiente y no se duplica.
    r = await cliente.post(LOGIN, json={"credential": "google:nuevo@example.org"})
    assert r.status_code == 403
    assert await db.usuarios.count_documents({}) == 1


async def test_login_usuario_activo_devuelve_tokens_y_perfil(cliente, crear_usuario):
    await crear_usuario("ana@example.org", google_id="gid-ana@example.org")

    r = await cliente.post(LOGIN, json={"credential": "google:ana@example.org"})

    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["usuario"]["email"] == "ana@example.org"
    assert cuerpo["usuario"]["ultimo_acceso"] is not None
    assert cuerpo["tokens"]["token_type"] == "bearer"
    assert cuerpo["tokens"]["expires_in"] == 1800

    r = await cliente.get(ME, headers={"Authorization": f'Bearer {cuerpo["tokens"]["access_token"]}'})
    assert r.status_code == 200
    assert r.json()["email"] == "ana@example.org"


async def test_login_vincula_google_a_un_alta_manual(cliente, crear_usuario, db):
    """Un usuario creado a mano por el administrador entra con Google por primera vez."""
    await crear_usuario("manual@example.org")

    r = await cliente.post(LOGIN, json={"credential": "google:manual@example.org"})

    assert r.status_code == 200
    usuario = await db.usuarios.find_one({"email": "manual@example.org"})
    assert usuario["google_id"] == "gid-manual@example.org"
    assert await db.usuarios.count_documents({}) == 1


async def test_login_usuario_inactivo_responde_403(cliente, crear_usuario):
    await crear_usuario("baja@example.org", estado=EstadoUsuario.INACTIVO)
    r = await cliente.post(LOGIN, json={"credential": "google:baja@example.org"})
    assert r.status_code == 403


async def test_login_con_credencial_falsa_responde_401(cliente):
    r = await cliente.post(LOGIN, json={"credential": "cualquier-cosa"})
    assert r.status_code == 401
    assert "detail" in r.json()


async def test_login_sin_credencial_responde_422(cliente):
    r = await cliente.post(LOGIN, json={})
    assert r.status_code == 422


async def test_peticion_sin_token_responde_401(cliente):
    r = await cliente.get(ME)
    assert r.status_code == 401
    assert r.json() == {"detail": "Token de autenticación ausente o inválido."}


async def test_token_manipulado_responde_401(cliente, profesor):
    token = servicio_auth.emitir_tokens(profesor).access_token
    r = await cliente.get(ME, headers={"Authorization": f"Bearer {token}x"})
    assert r.status_code == 401


async def test_token_caducado_responde_401(cliente, profesor):
    caducado = security._crear_token(str(profesor["_id"]), security.TIPO_ACCESS, timedelta(seconds=-1))
    r = await cliente.get(ME, headers={"Authorization": f"Bearer {caducado}"})
    assert r.status_code == 401


async def test_refresh_token_no_sirve_como_access_token(cliente, profesor):
    refresh = servicio_auth.emitir_tokens(profesor).refresh_token
    r = await cliente.get(ME, headers={"Authorization": f"Bearer {refresh}"})
    assert r.status_code == 401


async def test_usuario_desactivado_pierde_el_acceso_aunque_su_token_no_haya_caducado(cliente, profesor, db):
    token = cabeceras(profesor)
    assert (await cliente.get(ME, headers=token)).status_code == 200

    await db.usuarios.update_one({"_id": profesor["_id"]}, {"$set": {"estado": "inactivo"}})

    assert (await cliente.get(ME, headers=token)).status_code == 401


async def test_refresh_devuelve_tokens_nuevos_y_el_anterior_deja_de_servir(cliente, profesor):
    tokens = servicio_auth.emitir_tokens(profesor)

    r = await cliente.post(REFRESH, json={"refresh_token": tokens.refresh_token})
    assert r.status_code == 200
    nuevos = r.json()
    assert nuevos["refresh_token"] != tokens.refresh_token
    assert (await cliente.get(ME, headers={"Authorization": f'Bearer {nuevos["access_token"]}'})).status_code == 200

    # Rotación: el refresh token ya usado no se puede volver a usar.
    r = await cliente.post(REFRESH, json={"refresh_token": tokens.refresh_token})
    assert r.status_code == 401

    # El nuevo sí funciona.
    r = await cliente.post(REFRESH, json={"refresh_token": nuevos["refresh_token"]})
    assert r.status_code == 200


async def test_refresh_con_un_access_token_responde_401(cliente, profesor):
    tokens = servicio_auth.emitir_tokens(profesor)
    r = await cliente.post(REFRESH, json={"refresh_token": tokens.access_token})
    assert r.status_code == 401


async def test_refresh_de_usuario_desactivado_responde_401(cliente, profesor, db):
    tokens = servicio_auth.emitir_tokens(profesor)
    await db.usuarios.update_one({"_id": profesor["_id"]}, {"$set": {"estado": "inactivo"}})
    r = await cliente.post(REFRESH, json={"refresh_token": tokens.refresh_token})
    assert r.status_code == 401


async def test_logout_revoca_el_refresh_token(cliente, profesor):
    tokens = servicio_auth.emitir_tokens(profesor)
    auth = {"Authorization": f"Bearer {tokens.access_token}"}

    r = await cliente.post(LOGOUT, json={"refresh_token": tokens.refresh_token}, headers=auth)
    assert r.status_code == 204
    assert r.content == b""

    r = await cliente.post(REFRESH, json={"refresh_token": tokens.refresh_token})
    assert r.status_code == 401


async def test_logout_sin_token_responde_401(cliente):
    r = await cliente.post(LOGOUT, json={"refresh_token": "x"})
    assert r.status_code == 401


async def test_logout_no_revoca_el_refresh_token_de_otro_usuario(cliente, profesor, admin):
    tokens_admin = servicio_auth.emitir_tokens(admin)
    r = await cliente.post(LOGOUT, json={"refresh_token": tokens_admin.refresh_token}, headers=cabeceras(profesor))
    assert r.status_code == 204

    r = await cliente.post(REFRESH, json={"refresh_token": tokens_admin.refresh_token})
    assert r.status_code == 200
