# Módulo Web

Este módulo implementa la interfaz web para el sistema RAG de Moodle.

## Propósito

El módulo `web` proporciona una interfaz de usuario basada en web que permite:

1. Interactuar con el sistema RAG a través de un chat en el navegador
2. Ver y gestionar sesiones de chat anteriores
3. Crear nuevas sesiones de chat
4. Visualizar el historial de conversaciones

## Componentes

### app.py

Este archivo contiene la aplicación web Flask que:

- Crea y configura la aplicación Flask
- Define las rutas y endpoints para la interfaz web
- Genera dinámicamente las plantillas HTML si no existen
- Maneja la comunicación entre el frontend y el backend
- Integra el sistema RAG con la interfaz web

La aplicación web proporciona las siguientes rutas:

- `/`: Página principal con el chat interactivo
- `/chat`: Endpoint para procesar mensajes del chat (POST)
- `/sessions`: Lista de sesiones de chat
- `/session/<session_id>`: Ver una sesión específica
- `/new_session`: Crear una nueva sesión
- `/messages`: Obtener mensajes de la sesión actual (para AJAX)

## Plantillas

El módulo genera automáticamente las siguientes plantillas HTML:

- `base.html`: Plantilla base con la estructura común
- `index.html`: Página principal con el chat
- `sessions.html`: Lista de sesiones de chat
- `session.html`: Vista de una sesión específica

## Uso

### Iniciar la aplicación web

```python
from web.app import run_app

# Iniciar la aplicación web con configuración por defecto
run_app()

# O con configuración personalizada
run_app(host='127.0.0.1', port=8080, debug=False)
```

### Desde línea de comandos

```bash
# Usando el script principal
python main.py --web

# O directamente
python -m web.app
```

### Personalizar la aplicación

```python
from web.app import create_app

# Crear la aplicación con configuración personalizada
app = create_app('ruta/a/config.yaml')

# Añadir rutas o funcionalidades adicionales
@app.route('/custom')
def custom_route():
    return "Ruta personalizada"

# Ejecutar la aplicación
app.run(host='0.0.0.0', port=5000)
```

## Características

- Diseño responsivo con Bootstrap
- Actualización en tiempo real del chat con JavaScript
- Persistencia de sesiones entre visitas
- Visualización formateada de mensajes
- Indicador de carga durante la generación de respuestas

## Requisitos

- Flask
- Un navegador web moderno
- Conexión a los servicios backend (Qdrant, PostgreSQL, Ollama)