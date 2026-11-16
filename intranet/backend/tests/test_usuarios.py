"""Tests de gestión de usuarios y departamentos."""
import pytest
from bson import ObjectId

from app.models.usuario import EstadoUsuario, Rol
from tests.conftest import cabeceras

pytestmark = pytest.mark.anyio

USUARIOS = "/api/v1/usuarios"
ID_INEXISTENTE = "660e1d8f1b2c3d4e5f6a7b8c"


def datos_alta(departamento, **cambios):
    return {
        "email": "maria@example.org",
        "nombre": "María",
        "apellidos": "García",
        "departamento_id": str(departamento["_id"]),
        **cambios,
    }


async def test_crear_usuario_devuelve_201_location_y_valores_por_defecto(cliente, admin, departamento):
    r = await cliente.post(USUARIOS, json=datos_alta(departamento), headers=cabeceras(admin))

    assert r.status_code == 201
    usuario = r.json()
    assert r.headers["Location"] == f'/api/v1/usuarios/{usuario["id"]}'
    assert usuario["roles"] == ["profesor"]
    assert usuario["estado"] == "activo"
    assert usuario["departamento_nombre"] == "Informática"

    r = await cliente.get(r.headers["Location"], headers=cabeceras(admin))
    assert r.status_code == 200
    assert r.json() == usuario


async def test_crear_usuario_con_correo_repetido_responde_409(cliente, admin, departamento):
    await cliente.post(USUARIOS, json=datos_alta(departamento), headers=cabeceras(admin))
    # El correo no distingue mayúsculas de minúsculas.
    r = await cliente.post(USUARIOS, json=datos_alta(departamento, email="MARIA@example.org"), headers=cabeceras(admin))
    assert r.status_code == 409


async def test_crear_usuario_con_departamento_inexistente_responde_422(cliente, admin):
    r = await cliente.post(USUARIOS, json=datos_alta({"_id": ID_INEXISTENTE}), headers=cabeceras(admin))
    assert r.status_code == 422
    assert r.json()["detail"][0]["loc"] == ["body", "departamento_id"]


@pytest.mark.parametrize(
    "cambios",
    [{"email": "no-es-un-correo"}, {"roles": ["superusuario"]}, {"roles": []}, {"estado": "borrado"}, {"nombre": ""}],
)
async def test_crear_usuario_con_datos_no_validos_responde_422(cliente, admin, departamento, cambios):
    r = await cliente.post(USUARIOS, json=datos_alta(departamento, **cambios), headers=cabeceras(admin))
    assert r.status_code == 422


async def test_listar_usuarios_pagina_y_filtra(cliente, admin, crear_usuario):
    for i in range(12):
        await crear_usuario(f"profe{i:02d}@example.org")
    await crear_usuario("pendiente@example.org", estado=EstadoUsuario.PENDIENTE)
    await crear_usuario("rmi@example.org", roles=(Rol.PROFESOR, Rol.RESPONSABLE_RMI))
    auth = cabeceras(admin)

    r = await cliente.get(USUARIOS, headers=auth)
    pagina = r.json()
    assert r.status_code == 200
    assert (pagina["page"], pagina["limit"], pagina["total"]) == (1, 10, 15)
    assert len(pagina["items"]) == 10

    r = await cliente.get(USUARIOS, params={"page": 2, "limit": 10}, headers=auth)
    assert len(r.json()["items"]) == 5

    r = await cliente.get(USUARIOS, params={"estado": "pendiente_confirmacion"}, headers=auth)
    assert [u["email"] for u in r.json()["items"]] == ["pendiente@example.org"]

    r = await cliente.get(USUARIOS, params={"rol": "responsable_rmi"}, headers=auth)
    assert [u["email"] for u in r.json()["items"]] == ["rmi@example.org"]

    r = await cliente.get(USUARIOS, params={"busqueda": "PROFE0"}, headers=auth)
    assert r.json()["total"] == 10


@pytest.mark.parametrize("params", [{"limit": 51}, {"limit": 0}, {"page": 0}, {"estado": "otro"}])
async def test_listar_usuarios_con_parametros_no_validos_responde_422(cliente, admin, params):
    r = await cliente.get(USUARIOS, params=params, headers=cabeceras(admin))
    assert r.status_code == 422


async def test_usuario_inexistente_responde_404_e_id_mal_formado_422(cliente, admin):
    assert (await cliente.get(f"{USUARIOS}/{ID_INEXISTENTE}", headers=cabeceras(admin))).status_code == 404
    assert (await cliente.delete(f"{USUARIOS}/{ID_INEXISTENTE}", headers=cabeceras(admin))).status_code == 404
    assert (await cliente.get(f"{USUARIOS}/123", headers=cabeceras(admin))).status_code == 422


async def test_flujo_completo_de_alta_con_google_y_aprobacion(cliente, admin):
    """Autorregistro con Google -> pendiente -> el administrador aprueba -> ya puede entrar."""
    login = {"credential": "google:nueva@example.org"}
    assert (await cliente.post("/api/v1/auth/login/google", json=login)).status_code == 403

    r = await cliente.get(USUARIOS, params={"estado": "pendiente_confirmacion"}, headers=cabeceras(admin))
    pendiente = r.json()["items"][0]

    r = await cliente.patch(f'{USUARIOS}/{pendiente["id"]}', json={"estado": "activo"}, headers=cabeceras(admin))
    assert r.status_code == 200
    assert r.json()["estado"] == "activo"

    assert (await cliente.post("/api/v1/auth/login/google", json=login)).status_code == 200


async def test_transiciones_de_estado(cliente, admin, profesor):
    ruta = f'{USUARIOS}/{profesor["_id"]}'
    auth = cabeceras(admin)

    # activo -> pendiente_confirmacion no está permitido
    r = await cliente.patch(ruta, json={"estado": "pendiente_confirmacion"}, headers=auth)
    assert r.status_code == 409
    # activo -> activo tampoco es un cambio
    assert (await cliente.patch(ruta, json={"estado": "activo"}, headers=auth)).status_code == 409
    # activo -> inactivo -> activo sí
    assert (await cliente.patch(ruta, json={"estado": "inactivo"}, headers=auth)).status_code == 200
    assert (await cliente.patch(ruta, json={"estado": "activo"}, headers=auth)).status_code == 200


async def test_administrador_no_puede_bloquearse_a_si_mismo(cliente, admin, departamento):
    ruta = f'{USUARIOS}/{admin["_id"]}'
    auth = cabeceras(admin)

    assert (await cliente.patch(ruta, json={"estado": "inactivo"}, headers=auth)).status_code == 409
    assert (await cliente.delete(ruta, headers=auth)).status_code == 409
    assert (await cliente.put(f"{ruta}/roles", json={"roles": ["profesor"]}, headers=auth)).status_code == 409
    cuerpo = datos_alta(departamento, email="admin@example.org", roles=["profesor"], estado="activo")
    assert (await cliente.put(ruta, json=cuerpo, headers=auth)).status_code == 409

    # Añadirse roles conservando el de administrador sí está permitido.
    r = await cliente.put(f"{ruta}/roles", json={"roles": ["administrador", "direccion"]}, headers=auth)
    assert r.status_code == 200


async def test_reemplazar_y_eliminar_usuario(cliente, admin, profesor, departamento):
    ruta = f'{USUARIOS}/{profesor["_id"]}'
    cuerpo = datos_alta(departamento, email="nuevo.correo@example.org", roles=["profesor", "secretaria"], estado="activo")

    r = await cliente.put(ruta, json=cuerpo, headers=cabeceras(admin))
    assert r.status_code == 200
    assert r.json()["email"] == "nuevo.correo@example.org"
    assert r.json()["roles"] == ["profesor", "secretaria"]

    assert (await cliente.delete(ruta, headers=cabeceras(admin))).status_code == 204
    assert (await cliente.get(ruta, headers=cabeceras(admin))).status_code == 404


async def test_actualizar_mi_perfil_solo_cambia_datos_de_contacto(cliente, profesor):
    cuerpo = {"telefono": "+34 600 000 000", "biografia": "Tutor de 2º DAW", "roles": ["administrador"], "estado": "inactivo"}

    r = await cliente.put(f"{USUARIOS}/me", json=cuerpo, headers=cabeceras(profesor))

    assert r.status_code == 200
    perfil = r.json()
    assert perfil["telefono"] == "+34 600 000 000"
    assert perfil["biografia"] == "Tutor de 2º DAW"
    # Nadie puede darse roles ni cambiar su estado desde su perfil.
    assert perfil["roles"] == ["profesor"]
    assert perfil["estado"] == "activo"


async def test_departamentos_crear_listar_y_actualizar(cliente, admin, profesor, db):
    auth = cabeceras(admin)
    r = await cliente.post("/api/v1/departamentos", json={"codigo": "dep-mat", "nombre": "Matemáticas"}, headers=auth)
    assert r.status_code == 201
    departamento = r.json()
    assert departamento["codigo"] == "DEP-MAT"
    assert r.headers["Location"] == f'/api/v1/departamentos/{departamento["id"]}'

    r = await cliente.post("/api/v1/departamentos", json={"codigo": "DEP-MAT", "nombre": "Otro"}, headers=auth)
    assert r.status_code == 409

    cuerpo = {"codigo": "DEP-MAT", "nombre": "Matemáticas", "jefe_departamento_id": str(profesor["_id"])}
    r = await cliente.put(f'/api/v1/departamentos/{departamento["id"]}', json=cuerpo, headers=auth)
    assert r.status_code == 200
    assert r.json()["jefe_departamento_nombre"] == "Nombre Apellidos"

    cuerpo["jefe_departamento_id"] = ID_INEXISTENTE
    r = await cliente.put(f'/api/v1/departamentos/{departamento["id"]}', json=cuerpo, headers=auth)
    assert r.status_code == 422

    await db.usuarios.update_one({"_id": profesor["_id"]}, {"$set": {"departamento_id": ObjectId(departamento["id"])}})
    r = await cliente.get("/api/v1/departamentos", headers=cabeceras(profesor))
    assert r.json()["total"] == 1
    assert r.json()["items"][0]["miembros_count"] == 1

    assert (await cliente.get(f"/api/v1/departamentos/{ID_INEXISTENTE}", headers=auth)).status_code == 404
