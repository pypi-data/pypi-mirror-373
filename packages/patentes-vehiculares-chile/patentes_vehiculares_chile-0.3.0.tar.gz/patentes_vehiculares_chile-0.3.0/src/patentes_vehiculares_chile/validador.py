"""
Validador de patentes vehiculares chilenas.
"""

import re
from typing import Optional
from itertools import cycle

from .tipos import (
    TipoPatente, 
    TipoVehiculo,  # Agregar esta línea
    FORMATO_VEHICULO_ANTIGUO, 
    FORMATO_VEHICULO_NUEVO,
    FORMATO_MOTOCICLETA_ANTIGUO,
    FORMATO_MOTOCICLETA_NUEVO,
    FORMATO_VEHICULO_DIPLOMATICO,  # Agregar
    FORMATO_VEHICULO_CARABINEROS,  # Agregar
    FORMATO_VEHICULO_EJERCITO,     # Agregar
    FORMATO_VEHICULO_BOMBEROS      # Agregar
)


def es_formato_valido(patente: str) -> bool:
    """
    Verifica si una patente tiene un formato válido.
    
    Args:
        patente: La patente a validar
        
    Returns:
        True si el formato es válido, False en caso contrario
    """
    if not isinstance(patente, str):
        return False
    
    patente = patente.upper().strip()
    
    # Verificar formato vehículo antiguo
    if re.match(FORMATO_VEHICULO_ANTIGUO.patron, patente):
        return True
    
    # Verificar formato vehículo nuevo
    if re.match(FORMATO_VEHICULO_NUEVO.patron, patente):
        return True
    
    # Verificar formato motocicleta antiguo
    if re.match(FORMATO_MOTOCICLETA_ANTIGUO.patron, patente):
        return True
    
    # Verificar formato motocicleta nuevo
    if re.match(FORMATO_MOTOCICLETA_NUEVO.patron, patente):
        return True
    
    # # Verificar formato remolque
    # if re.match(FORMATO_REMOLQUE.patron, patente):
    #     return True
    
    return False


def detectar_tipo_patente(patente: str) -> Optional[TipoPatente]:
    """
    Detecta el tipo de patente basado en su formato.
    
    Args:
        patente: La patente a analizar
        
    Returns:
        El tipo de patente o None si no es válida
    """
    if not isinstance(patente, str):
        return None
    
    patente = patente.upper().strip()
    
    # Verificar formatos antiguos (vehículos y motocicletas)
    if re.match(FORMATO_VEHICULO_ANTIGUO.patron, patente) or re.match(FORMATO_MOTOCICLETA_ANTIGUO.patron, patente):
        return TipoPatente.ANTIGUA
    # Verificar formatos nuevos (vehículos y motocicletas)  
    elif re.match(FORMATO_VEHICULO_NUEVO.patron, patente) or re.match(FORMATO_MOTOCICLETA_NUEVO.patron, patente):
        return TipoPatente.NUEVA
    
    return None


def validar_patente(patente: str) -> bool:
    """
    Valida si una patente vehicular chilena es válida.
    
    Args:
        patente: La patente a validar
        
    Returns:
        True si la patente es válida, False en caso contrario
        
    Examples:
        >>> validar_patente("AB1234")
        True
        >>> validar_patente("BCDF12") 
        True
        >>> validar_patente("123ABC")
        False
    """
    return es_formato_valido(patente)


def limpiar_patente(patente: str) -> str:
    """
    Limpia y normaliza una patente removiendo espacios y convirtiendo a mayúsculas.
    
    Args:
        patente: La patente a limpiar
        
    Returns:
        La patente limpia y normalizada
    """
    if not isinstance(patente, str):
        raise ValueError("La patente debe ser una cadena de texto")
    
    return patente.upper().strip().replace(" ", "").replace("-", "").replace("_", "").replace(".", "").replace(",", "").replace(";", "").replace(":", "")

def calcular_dv(rut_num: str) -> str:
    """
    Calcula el dígito verificador (DV) para un RUT chileno.

    Args:
        rut_num: El número de RUT (sin DV)

    Returns:
        El dígito verificador como str ('0'-'9' o 'K')
    """
    revertido = map(int, reversed(rut_num))
    factors = cycle(range(2, 8))
    suma = sum(d * f for d, f in zip(revertido, factors))
    residuo = suma % 11
    if residuo == 0:
        return '0'
    elif residuo == 1:
        return 'K'
    else:
        return str(11 - residuo)


def validar_rut(rut: str) -> bool:
    """
    Valida si un RUT chileno es válido.

    Args:
        rut: El RUT a validar

    Returns:
        True si el RUT es válido, False en caso contrario
    """
    if not isinstance(rut, str):
        return False

    rut = rut.upper().replace("-", "").replace(".", "").strip()
    if len(rut) < 2:
        return False

    rut_aux = rut[:-1]
    dv = rut[-1]

    if not rut_aux.isdigit() or not (1_000_000 <= int(rut_aux) <= 25_000_000):
        return False

    dv_calculado = calcular_dv(rut_aux)
    return dv == dv_calculado


def detectar_tipo_vehiculo(patente: str) -> TipoVehiculo:
    """
    Detecta el tipo específico de vehículo basado en su patente.
    
    Args:
        patente: La patente a analizar
        
    Returns:
        El tipo específico de vehículo
        
    Examples:
        >>> detectar_tipo_vehiculo("AB1234")
        TipoVehiculo.VEHICULO_ANTIGUO
        >>> detectar_tipo_vehiculo("BCDF12") 
        TipoVehiculo.VEHICULO_NUEVO
        >>> detectar_tipo_vehiculo("CD1234")
        TipoVehiculo.DIPLOMATICO
        >>> detectar_tipo_vehiculo("RP1234")
        TipoVehiculo.CARABINEROS
    """
    if not isinstance(patente, str):
        return TipoVehiculo.DESCONOCIDO
    
    patente = patente.upper().strip()
    
    # Verificar formatos especiales primero (más específicos)
    if re.match(FORMATO_VEHICULO_DIPLOMATICO.patron, patente):
        return TipoVehiculo.DIPLOMATICO
    
    if re.match(FORMATO_VEHICULO_CARABINEROS.patron, patente):
        return TipoVehiculo.CARABINEROS
    
    if re.match(FORMATO_VEHICULO_EJERCITO.patron, patente):
        return TipoVehiculo.EJERCITO
    
    if re.match(FORMATO_VEHICULO_BOMBEROS.patron, patente):
        return TipoVehiculo.BOMBEROS
    
    # Verificar formatos civiles
    if re.match(FORMATO_VEHICULO_ANTIGUO.patron, patente):
        return TipoVehiculo.VEHICULO_ANTIGUO
    
    if re.match(FORMATO_VEHICULO_NUEVO.patron, patente):
        return TipoVehiculo.VEHICULO_NUEVO
    
    if re.match(FORMATO_MOTOCICLETA_ANTIGUO.patron, patente):
        return TipoVehiculo.MOTOCICLETA_ANTIGUA
    
    if re.match(FORMATO_MOTOCICLETA_NUEVO.patron, patente):
        return TipoVehiculo.MOTOCICLETA_NUEVA
    
    return TipoVehiculo.DESCONOCIDO