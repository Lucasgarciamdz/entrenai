# Módulo Core

Este módulo contiene las funcionalidades centrales del sistema RAG para Moodle.

## Propósito

El módulo `core` proporciona la infraestructura básica que utilizan todos los demás módulos del sistema, incluyendo:

- Gestión de configuración
- Manejo de errores personalizados
- Utilidades generales y configuración de logging

## Componentes

### config.py

Este archivo maneja la carga de configuración desde archivos YAML y variables de entorno. Proporciona funciones para:

- Cargar configuración desde un archivo YAML
- Aplicar variables de entorno sobre la configuración cargada
- Guardar una configuración por defecto

### errors.py

Define las clases de errores personalizados para el sistema RAG:

- `ErrorRAG`: Error base para el sistema
- `ErrorMoodle`: Error al interactuar con Moodle
- `ErrorProcesamientoDocumento`: Error en el procesamiento de documentos
- `ErrorVectorDB`: Error en la base de datos vectorial
- `ErrorChat`: Error en el gestor de chat

### utils.py

Proporciona utilidades generales para el sistema, principalmente:

- Configuración de logging centralizada
- Funciones auxiliares reutilizables

## Uso

Los componentes de este módulo son utilizados por todos los demás módulos del sistema. Por ejemplo:

```python
from core.config import load_config
from core.errors import ErrorRAG
from core.utils import configurar_logging

# Cargar configuración
config = load_config('config.yaml')

# Configurar logging
logger = configurar_logging('mi_modulo')

# Manejar errores
try:
    # Alguna operación
    pass
except Exception as e:
    raise ErrorRAG(f"Error en la operación: {e}")
```