"""Valores permitidos y reglas del documento `usuarios`."""
from enum import StrEnum


class Rol(StrEnum):
    PROFESOR = "profesor"
    ADMINISTRADOR = "administrador"
    JEFATURA_ESTUDIOS = "jefatura_estudios"
    SECRETARIA = "secretaria"
    RESPONSABLE_RMI = "responsable_rmi"
    ADMIN_RRSS = "admin_rrss"
    DIRECCION = "direccion"


class EstadoUsuario(StrEnum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    PENDIENTE = "pendiente_confirmacion"


# Cambios de estado permitidos: desde -> hacia.
# Una cuenta nunca vuelve a "pendiente_confirmacion".
TRANSICIONES_ESTADO = {
    EstadoUsuario.PENDIENTE: {EstadoUsuario.ACTIVO, EstadoUsuario.INACTIVO},
    EstadoUsuario.ACTIVO: {EstadoUsuario.INACTIVO},
    EstadoUsuario.INACTIVO: {EstadoUsuario.ACTIVO},
}
