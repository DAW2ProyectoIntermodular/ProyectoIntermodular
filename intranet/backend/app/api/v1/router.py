"""Agrupa todos los endpoints de la versión 1 de la API bajo /api/v1."""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, departamentos, usuarios

router_v1 = APIRouter(prefix="/api/v1")
router_v1.include_router(auth.router)
router_v1.include_router(usuarios.router)
router_v1.include_router(departamentos.router)
