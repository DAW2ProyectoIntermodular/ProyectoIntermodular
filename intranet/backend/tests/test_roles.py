"""Tests del control de acceso por roles."""
import pytest

from app.models.usuario import Rol
from tests.conftest import cabeceras

pytestmark = pytest.mark.anyio

ID_CUALQUIERA = "660e1d8f1b2c3d4e5f6a7b8c"

# (método, ruta, cuerpo) de las operaciones reservadas al administrador
SOLO_ADMINISTRADOR = [
    ("POST", "/api/v1/usuarios", {"email": "x@example.org", "nombre": "X", "apellidos": "Y", "departamento_id": ID_CUALQUIERA}),
    ("PUT", f"/api/v1/usuarios/{ID_CUALQUIERA}", {"email": "x@example.org", "nombre": "X", "apellidos": "Y", "departamento_id": ID_CUALQUIERA, "roles": ["profesor"], "estado": "activo"}),
    ("PATCH", f"/api/v1/usuarios/{ID_CUALQUIERA}", {"estado": "activo"}),
    ("DELETE", f"/api/v1/usuarios/{ID_CUALQUIERA}", None),
    ("PUT", f"/api/v1/usuarios/{ID_CUALQUIERA}/roles", {"roles": ["administrador"]}),
    ("POST", "/api/v1/departamentos", {"codigo": "DEP-X", "nombre": "X"}),
    ("PUT", f"/api/v1/departamentos/{ID_CUALQUIERA}", {"codigo": "DEP-X", "nombre": "X"}),
]


@pytest.mark.parametrize("metodo,ruta,cuerpo", SOLO_ADMINISTRADOR)
@pytest.mark.parametrize("rol", [Rol.PROFESOR, Rol.JEFATURA_ESTUDIOS, Rol.DIRECCION])
async def test_operaciones_de_administrador_prohibidas_para_otros_roles(cliente, crear_usuario, metodo, ruta, cuerpo, rol):
    usuario = await crear_usuario(roles=(rol,))
    r = await cliente.request(metodo, ruta, json=cuerpo, headers=cabeceras(usuario))
    assert r.status_code == 403
    assert r.json() == {"detail": "No dispone de los permisos necesarios para realizar esta acción."}


@pytest.mark.parametrize("metodo,ruta,cuerpo", SOLO_ADMINISTRADOR)
async def test_operaciones_de_administrador_sin_token_responden_401(cliente, metodo, ruta, cuerpo):
    r = await cliente.request(metodo, ruta, json=cuerpo)
    assert r.status_code == 401


async def test_profesor_no_puede_listar_ni_consultar_usuarios(cliente, profesor):
    assert (await cliente.get("/api/v1/usuarios", headers=cabeceras(profesor))).status_code == 403
    ruta = f'/api/v1/usuarios/{profesor["_id"]}'
    assert (await cliente.get(ruta, headers=cabeceras(profesor))).status_code == 403


async def test_jefatura_puede_listar_y_consultar_usuarios(cliente, crear_usuario, profesor):
    jefatura = await crear_usuario("jefatura@example.org", roles=(Rol.PROFESOR, Rol.JEFATURA_ESTUDIOS))
    assert (await cliente.get("/api/v1/usuarios", headers=cabeceras(jefatura))).status_code == 200
    ruta = f'/api/v1/usuarios/{profesor["_id"]}'
    assert (await cliente.get(ruta, headers=cabeceras(jefatura))).status_code == 200


async def test_cualquier_usuario_autenticado_ve_su_perfil_y_los_departamentos(cliente, profesor):
    assert (await cliente.get("/api/v1/usuarios/me", headers=cabeceras(profesor))).status_code == 200
    assert (await cliente.get("/api/v1/departamentos", headers=cabeceras(profesor))).status_code == 200


async def test_un_cambio_de_roles_tiene_efecto_inmediato(cliente, profesor, admin):
    """Los roles se leen de la base de datos en cada petición, no del token."""
    token_profesor = cabeceras(profesor)
    assert (await cliente.get("/api/v1/usuarios", headers=token_profesor)).status_code == 403

    r = await cliente.put(
        f'/api/v1/usuarios/{profesor["_id"]}/roles',
        json={"roles": ["profesor", "jefatura_estudios"]},
        headers=cabeceras(admin),
    )
    assert r.status_code == 200

    assert (await cliente.get("/api/v1/usuarios", headers=token_profesor)).status_code == 200
