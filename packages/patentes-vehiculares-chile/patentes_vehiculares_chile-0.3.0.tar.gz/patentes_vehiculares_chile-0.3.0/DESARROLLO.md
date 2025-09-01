# Guía de Desarrollo y Publicación

Esta guía te ayudará a desarrollar, probar y publicar la librería.

## Configuración del Entorno de Desarrollo

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Activar entorno virtual (Linux/Mac)
source venv/bin/activate

# Instalar dependencias de desarrollo
pip install -e ".[dev]"
```

## Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests con cobertura
pytest --cov=patentes_vehiculares_chile --cov-report=html

# Ejecutar tests específicos
pytest tests/test_validador.py
```

## Formato y Linting

```bash
# Formatear código
black src/ tests/ examples/

# Verificar código
flake8 src/ tests/ examples/

# Verificar tipos
mypy src/
```

## Construir la Librería

```bash
# Instalar herramientas de construcción
pip install build twine

# Construir la librería
python -m build

# Verificar la construcción
twine check dist/*
```

## Publicar en PyPI

### Test PyPI (recomendado primero)

```bash
# Subir a Test PyPI
twine upload --repository testpypi dist/*

# Probar instalación desde Test PyPI
pip install --index-url https://test.pypi.org/simple/ patentes-vehiculares-chile
```

### PyPI Producción

```bash
# Subir a PyPI
twine upload dist/*

# Probar instalación desde PyPI
pip install patentes-vehiculares-chile
```

## Flujo de Desarrollo Recomendado

1. **Desarrollar**: Hacer cambios en el código
2. **Probar**: Ejecutar tests localmente
3. **Formatear**: Usar black y verificar con flake8
4. **Documentar**: Actualizar README y CHANGELOG
5. **Versionar**: Actualizar versión en pyproject.toml
6. **Construir**: Generar distribución
7. **Publicar**: Subir a PyPI

## Comandos Útiles

```bash
# Instalar en modo de desarrollo
pip install -e .

# Ejecutar ejemplo básico
python examples/ejemplo_basico.py

# Ejecutar ejemplo avanzado
python examples/ejemplo_avanzado.py

# Verificar instalación
python -c "import patentes_vehiculares_chile; print('OK')"
```
