"""
Patentes Vehiculares Chile

Una librería Python para validar y trabajar con patentes vehiculares chilenas.
"""

__version__ = "0.3.0"
__author__ = "Jorge Gallardo"
__email__ = "jorgito899@gmail.com"

from .validador import (
    validar_patente, 
    es_formato_valido, 
    detectar_tipo_patente, 
    detectar_tipo_vehiculo,  # Agregar esta línea
    limpiar_patente
)
from .tipos import TipoPatente, TipoVehiculo, FormatoPatente  # Agregar TipoVehiculo

from .generador import (
    generar_patente_vehiculo_antiguo,
    generar_patente_vehiculo_nuevo,
    generar_patente_motocicleta_antigua,
    generar_patente_motocicleta_nueva,
    generar_rut
)

__all__ = [
    "validar_patente",
    "es_formato_valido",
    "detectar_tipo_patente",
    "detectar_tipo_vehiculo",  # Agregar
    "limpiar_patente", 
    "TipoPatente",
    "TipoVehiculo",  # Agregar
    "FormatoPatente",
    "calcular_dv",
    "validar_rut"
]