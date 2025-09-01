# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto se adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [No publicado]

### Planificado
- Soporte para patentes de remolques
- Validación de patentes extranjeras
- API REST para validación en línea

## [0.3.0] - 2025-08-31

### Agregado
- 🎉 **Nueva función `detectar_tipo_vehiculo()`** para identificar tipos específicos de vehículos
- Soporte para patentes diplomáticas (CD, OI)
- Soporte para patentes de Carabineros (RP, M, AP, Z, B, etc.)
- Soporte para patentes del Ejército (EJTO)
- Soporte para patentes de Bomberos (CB)
- Nuevo enum `TipoVehiculo` con categorías específicas
- Formatos de validación para vehículos especiales
- Documentación expandida con ejemplos de patentes especiales

### Mejorado
- Patrones regex más precisos para cada tipo de vehículo
- Documentación del API más detallada
- Ejemplos de uso más completos en README

### Corregido
- Corrección en validación de RUT con dígito verificador '0'
- Mejoras en la limpieza de patentes con caracteres especiales

## [0.2.0] - 2025-07-31

### Agregado (v0.2.0)
- Funcionalidad inicial para validar patentes vehiculares chilenas
- Soporte para formatos antiguos (AB1234) y nuevos (ABCD12)
- Generador de patentes aleatorias válidas
- Función para detectar el tipo de patente
- Utilidad para limpiar y normalizar patentes
- Soporte para formatos de motocicletas
- Validación y generación de RUT chilenos

## [0.1.0] - 2025-07-29

### Agregado (v0.1.0)
- Primera versión de la librería
- Validación básica de patentes vehiculares chilenas
- Generación de patentes aleatorias básica
- Documentación inicial
- Estructura base del proyecto