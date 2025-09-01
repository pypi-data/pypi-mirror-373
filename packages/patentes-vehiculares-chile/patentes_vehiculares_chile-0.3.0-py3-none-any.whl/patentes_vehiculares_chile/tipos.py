"""
Tipos de datos para patentes vehiculares chilenas.
"""

from enum import Enum
from typing import NamedTuple


class TipoPatente(Enum):
    """Tipos de patentes vehiculares en Chile."""
    ANTIGUA = "antigua"  # Formato: AB1234
    NUEVA = "nueva"      # Formato: ABCD12


class TipoVehiculo(Enum):
    """Tipos específicos de vehículos según su patente."""
    VEHICULO_ANTIGUO = "vehiculo_antiguo"
    VEHICULO_NUEVO = "vehiculo_nuevo"
    MOTOCICLETA_ANTIGUA = "motocicleta_antigua"
    MOTOCICLETA_NUEVA = "motocicleta_nueva"
    DIPLOMATICO = "diplomatico"
    CARABINEROS = "carabineros"
    EJERCITO = "ejercito"
    BOMBEROS = "bomberos"
    DESCONOCIDO = "desconocido"


class FormatoPatente(NamedTuple):
    """Estructura que define el formato de una patente."""
    patron: str
    longitud: int
    descripcion: str

class FormatoRut(NamedTuple):
    """Estructura que define el formato de un RUT chileno."""
    patron: str
    longitud: int
    descripcion: str

# Formatos de patentes chilenas 1845-2007
FORMATO_VEHICULO_ANTIGUO= FormatoPatente(
    # De acuerdo a la normativa chilena, las PPU antiguas deben tener 2 letras y 4 números
    patron=r"^[ABCDEFGHKLNMOPRSTUVWXYZ][ABCDEFGHIJKLNPRSTUVXYZW][1-9][0-9]{3}$",
    longitud=6,
    descripcion="Formato antiguo: 2 letras + 4 números (ej: AB1234)"
)

# Formatos de patentes chilenas 2008-2023
FORMATO_VEHICULO_NUEVO = FormatoPatente(
    # De acuerdo a la normativa chilena, las letras deben ser consonantes y no vocales, además de dejar de lado
    # las letras M, N, Ñ y Q para evitar confusiones y que se generen siglas groseras.
    patron=r"^[BCDFGHJKLPRSTVWXYZ]{4}[1-9][0-9]{1}$",
    longitud=6,
    descripcion="Formato nuevo: 4 letras + 2 números (ej: BCDF12)"
)

# Formato antiguo de patentes de motocicletas chilenas
FORMATO_MOTOCICLETA_ANTIGUO = FormatoPatente(
    # Formato específico para motocicletas, que puede variar según normativa
    patron=r"^[BCDFGHJKLPRSTVWXYZ]{2}[1-9][0-9]{2}$",
    longitud=5,
    descripcion="Formato motocicleta: 2 letras + 3 números (ej: AB123)"
)

# Formato nuevo de patentes de motocicletas chilenas
FORMATO_MOTOCICLETA_NUEVO = FormatoPatente(
    # Formato específico para motocicletas, que puede variar según normativa
    # Pueden contener M, N y Q
    patron=r"^[BCDFGHJKLKMNPQRSTVWXYZ]{3}[1-9][0-9]$",
    longitud=5,
    descripcion="Formato motocicleta: 3 letras + 2 números (ej: ABC12)"
)

# Formato vehículos del cuerpo diplomático
FORMATO_VEHICULO_DIPLOMATICO = FormatoPatente(
    # Comienzan por CD u OI
    patron=r"^(CD|OI)[0-9]{4}$",
    longitud=6,
    descripcion="Formato diplomático: CD/OI + 4 números (ej: CD1234, OI5678)"
)

# Formato vehículos pertenecientes a carabineros
FORMATO_VEHICULO_CARABINEROS = FormatoPatente(
    # Comienzan con las siguientes letras según tipo de vehículo
    patron=r"^(M|AP|Z|B|RP|LA|AG|C|J|TC|CR|A|CB|F)[0-9]{3,4}$",
    longitud=5-6,  # Corrección: varía entre 5-6 caracteres
    descripcion="Formato carabineros: código + 4 números (ej: RP1234, M5678)"
)

# Vehículos del Ejército de Chile
FORMATO_VEHICULO_EJERCITO = FormatoPatente(
    # Comienzan con las letras EJTO
    patron=r"^(EJTO)[0-9]{2}$",
    longitud=6,
    descripcion="Formato ejército: EJTO + 2 números (ej: EJTO12)"
)

# Vehículos del Cuerpo de Bomberos
FORMATO_VEHICULO_BOMBEROS = FormatoPatente(
    # Comienzan con las letras CB
    patron=r"^(CB)[A-Z][0-9]{3}$",
    longitud=6,
    descripcion="Formato bomberos: CB + 1 letra + 3 números (ej: CBA123)"
)

FORMATO_RUT = FormatoRut(
    # Formato específico para RUT chileno
    patron=r"^\d{1,8}-[0-9K]$",
    longitud=10,
    descripcion="Formato RUT: 1-8 dígitos + guion + dígito verificador (ej: 12345678-K)"
)