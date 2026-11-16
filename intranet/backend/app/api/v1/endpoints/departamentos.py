"""Endpoints de departamentos didácticos."""
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.core.database import get_db
from app.core.permisos import UsuarioActual, requiere_roles
from app.models.usuario import Rol
from app.schemas.comun import IdRuta, Limite_, Pagina, Pagina_
from app.schemas.departamento import Departamento, DepartamentoCrear
from app.services import departamentos as servicio

router = APIRouter(prefix="/departamentos", tags=["Departamentos"])

SoloAdmin = Annotated[dict, Depends(requiere_roles(Rol.ADMINISTRADOR))]


@router.get("", response_model=Pagina[Departamento], summary="Listar departamentos")
async def listar_departamentos(_: UsuarioActual, db=Depends(get_db), page: Pagina_ = 1, limit: Limite_ = 10):
    items, total = await servicio.listar(db, page, limit)
    return Pagina(items=items, page=page, limit=limit, total=total)


@router.post(
    "", response_model=Departamento, status_code=status.HTTP_201_CREATED, summary="Crear departamento"
)
async def crear_departamento(cuerpo: DepartamentoCrear, response: Response, _: SoloAdmin, db=Depends(get_db)):
    departamento = await servicio.crear(db, cuerpo)
    response.headers["Location"] = f"/api/v1/departamentos/{departamento.id}"
    return departamento


@router.get("/{departamento_id}", response_model=Departamento, summary="Obtener detalle de un departamento")
async def obtener_departamento(departamento_id: IdRuta, _: UsuarioActual, db=Depends(get_db)):
    return await servicio.obtener(db, departamento_id)


@router.put("/{departamento_id}", response_model=Departamento, summary="Actualizar departamento")
async def actualizar_departamento(
    departamento_id: IdRuta, cuerpo: DepartamentoCrear, _: SoloAdmin, db=Depends(get_db)
):
    return await servicio.actualizar(db, departamento_id, cuerpo)
