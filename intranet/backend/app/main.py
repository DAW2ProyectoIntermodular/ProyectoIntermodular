"""Punto de entrada de la API de la intranet."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router_v1
from app.core import cache, database
from app.core.config import get_ajustes
from app.core.errores import DatoNoValido, ErrorNegocio
from app.services.usuarios import crear_primer_administrador

log = logging.getLogger("intranet")


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    """Al arrancar: conecta con MongoDB y Redis, crea índices y el primer administrador."""
    ajustes = get_ajustes()
    database.conectar()
    cache.conectar()
    db = database.get_db()
    await database.crear_indices(db)
    if ajustes.primer_admin_email and await crear_primer_administrador(db, ajustes.primer_admin_email):
        log.info("Creado el administrador inicial: %s", ajustes.primer_admin_email)
    yield
    await cache.desconectar()
    await database.desconectar()


def crear_app() -> FastAPI:
    ajustes = get_ajustes()
    app = FastAPI(
        title="Intranet de Gestión Docente - IES Ramón Arcas Meca",
        version="1.0.0",
        description="API de la intranet. El contrato completo está en docs/api/openapi-intranet.yaml.",
        lifespan=ciclo_de_vida,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ajustes.lista_cors,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Location"],
    )

    @app.exception_handler(ErrorNegocio)
    async def manejar_error_negocio(_: Request, error: ErrorNegocio):
        cabeceras = {"WWW-Authenticate": "Bearer"} if error.codigo_http == 401 else None
        return JSONResponse(status_code=error.codigo_http, content={"detail": error.detalle}, headers=cabeceras)

    @app.exception_handler(DatoNoValido)
    async def manejar_dato_no_valido(_: Request, error: DatoNoValido):
        detalle = [{"loc": ["body", error.campo], "msg": error.mensaje, "type": "value_error"}]
        return JSONResponse(status_code=422, content={"detail": detalle})

    @app.get("/salud", tags=["Sistema"], summary="Comprobar que la API está en marcha")
    async def salud():
        return {"estado": "ok"}

    app.include_router(router_v1)
    return app


app = crear_app()
