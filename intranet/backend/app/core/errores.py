"""Errores de negocio. Los servicios los lanzan y main.py los convierte en respuestas HTTP
con el formato del contrato: {"detail": "..."}."""


class ErrorNegocio(Exception):
    codigo_http = 400

    def __init__(self, detalle: str):
        super().__init__(detalle)
        self.detalle = detalle


class NoAutenticado(ErrorNegocio):
    codigo_http = 401


class AccesoDenegado(ErrorNegocio):
    codigo_http = 403


class NoEncontrado(ErrorNegocio):
    codigo_http = 404


class Conflicto(ErrorNegocio):
    codigo_http = 409


class DatoNoValido(Exception):
    """Un campo del cuerpo es incorrecto por una regla que Pydantic no puede comprobar
    (por ejemplo, un departamento que no existe). Se responde 422 con el formato de FastAPI."""

    def __init__(self, campo: str, mensaje: str):
        super().__init__(mensaje)
        self.campo = campo
        self.mensaje = mensaje
