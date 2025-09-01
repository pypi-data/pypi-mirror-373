# Script para generar patentes vehiculares chilenas
import random
from .validador import calcular_dv
"""Generador de patentes vehiculares chilenas.
"""

# Generar patente vehiculo antiguo
def generar_patente_vehiculo_antiguo() -> str:
    return f"{random.choice('ABCDEFGHKLNMOPRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLNPRSTUVXYZW')}{random.randint(1000, 9999)}"

# Generar patente vehiculo nuevo
def generar_patente_vehiculo_nuevo() -> str:
    consonantes = 'BCDFGHJKLPRSTVWXYZ'
    return f"{''.join(random.choice(consonantes) for _ in range(4))}{random.randint(10, 99)}"

# Generar patente motocicleta antigua
def generar_patente_motocicleta_antigua() -> str:
    return f"{random.choice('BCDFGHJKLPRSTVWXYZ')}{random.choice('BCDFGHJKLPRSTVWXYZ')}{random.randint(100, 999)}"

# Generar patente motocicleta nueva
def generar_patente_motocicleta_nueva() -> str:
    return f"{random.choice('BCDFGHJKLKMNPQRSTVWXYZ')}{random.choice('BCDFGHJKLKMNPQRSTVWXYZ')}{random.randint(100, 999)}"

# Generar patente cuerpo diplomático
def generar_patente_diplomatico() -> str:
    prefijos = ['CD', 'OI']
    return f"{random.choice(prefijos)}{random.randint(1000, 9999)}"

# Generar patente vehículo Carabineros
def generar_patente_carabineros() -> str:
    codigos = ['M', 'AP', 'Z', 'B', 'RP', 'LA', 'AG', 'C', 'J', 'TC', 'CR', 'A', 'CB', 'F']
    codigo = random.choice(codigos)
    cantidad_digitos = random.choice([3, 4])
    numeros = random.randint(10**(cantidad_digitos-1), 10**cantidad_digitos-1)
    return f"{codigo}{numeros}"

# Generar patente vehículo Ejército de Chile
def generar_patente_ejercito() -> str:
    return f"EJTO{random.randint(10, 99)}"

# Generar patente vehículo Bomberos
def generar_patente_bomberos() -> str:
    letra = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    numeros = random.randint(100, 999)
    return f"CB{letra}{numeros}"

# Generar RUT chileno
def generar_rut() -> str:
    numero = random.randint(3000000, 25999999)
    digito_verificador = calcular_dv(str(numero))
    return f"{numero}-{digito_verificador}"