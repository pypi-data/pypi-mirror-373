# Crewmaster

Orchestrates interactions between AI agents, with built-in LLM vendor independence.

## Getting Started

```
pip install crewmaster
```

## Variables de entorno

Necesitas crear un archivo .env con las siguientes variables de entorno de openai

```
LLM_API_KEY_OPEN_AI=DEFAULT
LLM_MODEL_OPEN_AI="gpt-3.5-turbo"
LLM_TEMPERATURE_OPEN_AI=0
```

## Instalar dependencias

1. Activar entorno virtual
```
poetry env use python
```
2. Instalar
```
poetry install
```

## Ejecutar los test 

1. Ejecutar todos los test
```
poetry run pytest
```

2. Se puede utilizar pytest para hacer los tests:
```
poetry run pytest ./ruta/a/probar --capture=no
```

3. Pytest no ofrece un modo "watch".  Si quiere utilizar un modo watch debes  ejecutar:
```
poetry run ptw ./ruta/a/monitorear ./ruta/a/probar --capture=no
```

4. Si se quiere probar sólo algún test, se puede agregar la marca `@pytest.mark.mi_marca` y luego ejecutar con el parámetro -k=mi_marca.

```
# test.py
@pytest.mark.mi_marca
def test_check...

# console
poetry run ptw ./ruta/a/monitorear ./ruta/a/probar --capture=no -k=mi_marca
```

Publicación en pypi
=====

La librería se publica automáticamente en Pypi con cada merge que se hace en los branchs de develop (beta) y master (production).

Puedes ver más información en la [documentación para pypi](docs/pypi.md).