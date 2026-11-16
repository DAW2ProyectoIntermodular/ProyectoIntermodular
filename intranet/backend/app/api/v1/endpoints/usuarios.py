"""Endpoints de usuarios."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.database import get_db
from app.core.permisos import UsuarioActual, requiere_roles
from app.models.usuario import EstadoUsuario, Rol
from app.schemas.comun import PATRON_OBJECT_ID, IdRuta, Limite_, Pagina, Pagina_
from app.schemas.usuario import (
    Usuario,
    UsuarioActualizar,
    UsuarioCrear,
    UsuarioEstadoPatch,
    UsuarioPerfilActualizar,
    UsuarioRolesPut,
)
from app.services import usuarios as servicio

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

SoloAdmin = Annotated[dict, Depends(requiere_roles(Rol.ADMINISTRADOR))]
AdminOJefatura = Annotated[dict, Depends(requiere_roles(Rol.ADMINISTRADOR, Rol.JEFATURA_ESTUDIOS))]


# Las rutas /me van antes que /{usuario_id} para que "me" no se tome por un identificador.
@router.get("/me", response_model=Usuario, summary="Obtener perfil del usuario autenticado")
async def mi_perfil(usuario: UsuarioActual, db=Depends(get_db)):
    return await servicio.a_esquema_completo(db, usuario)


@router.put("/me", response_model=Usuario, summary="Actualizar datos personales del usuario autenticado")
async def actualizar_mi_perfil(cuerpo: UsuarioPerfilActualizar, usuario: UsuarioActual, db=Depends(get_db)):
    return await servicio.actualizar_perfil(db, usuario, cuerpo)


@router.get("", response_model=Pagina[Usuario], summary="Listar usuarios con filtros y paginación")
async def listar_usuarios(
    _: AdminOJefatura,
    db=Depends(get_db),
    estado: EstadoUsuario | None = None,
    rol: Rol | None = None,
    departamento_id: Annotated[str | None, Query(pattern=PATRON_OBJECT_ID)] = None,
    busqueda: str | None = None,
    page: Pagina_ = 1,
    limit: Limite_ = 10,
):
    items, total = await servicio.listar(
        db, page=page, limit=limit, estado=estado, rol=rol, departamento_id=departamento_id, busqueda=busqueda
    )
    return Pagina(items=items, page=page, limit=limit, total=total)


@router.post(
    "", response_model=Usuario, status_code=status.HTTP_201_CREATED, summary="Crear usuario manualmente"
)
async def crear_usuario(cuerpo: UsuarioCrear, response: Response, _: SoloAdmin, db=Depends(get_db)):
    usuario = await servicio.crear(db, cuerpo)
    response.headers["Location"] = f"/api/v1/usuarios/{usuario.id}"
    return usuario


@router.get("/{usuario_id}", response_model=Usuario, summary="Obtener detalle de un usuario")
async def obtener_usuario(usuario_id: IdRuta, _: AdminOJefatura, db=Depends(get_db)):
    return await servicio.obtener(db, usuario_id)


@router.put("/{usuario_id}", response_model=Usuario, summary="Actualizar usuario completo")
async def reemplazar_usuario(usuario_id: IdRuta, cuerpo: UsuarioActualizar, admin: SoloAdmin, db=Depends(get_db)):
    return await servicio.reemplazar(db, usuario_id, cuerpo, admin)


@router.patch("/{usuario_id}", response_model=Usuario, summary="Cambiar estado o aprobar registro")
async def cambiar_estado_usuario(
    usuario_id: IdRuta, cuerpo: UsuarioEstadoPatch, admin: SoloAdmin, db=Depends(get_db)
):
    return await servicio.cambiar_estado(db, usuario_id, cuerpo, admin)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar usuario")
async def eliminar_usuario(usuario_id: IdRuta, admin: SoloAdmin, db=Depends(get_db)):
    await servicio.eliminar(db, usuario_id, admin)


@router.put("/{usuario_id}/roles", response_model=Usuario, summary="Asignar o reemplazar roles de un usuario")
async def cambiar_roles_usuario(usuario_id: IdRuta, cuerpo: UsuarioRolesPut, admin: SoloAdmin, db=Depends(get_db)):
    return await servicio.cambiar_roles(db, usuario_id, cuerpo.roles, admin)
