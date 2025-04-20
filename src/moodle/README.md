# Módulo Moodle

Este módulo proporciona funcionalidades para interactuar con la plataforma Moodle.

## Propósito

El módulo `moodle` permite al sistema RAG conectarse a una instancia de Moodle, obtener información sobre cursos y contenidos, y descargar archivos para su posterior procesamiento e indexación.

## Componentes

### client.py

Este archivo implementa un cliente para la API REST de Moodle. Proporciona funcionalidades para:

- Autenticarse con un token de API
- Obtener la lista de cursos disponibles
- Obtener el contenido de un curso específico
- Descargar archivos de Moodle

La clase principal `MoodleClient` maneja todas las comunicaciones con la API de Moodle, incluyendo:

- Gestión de errores de comunicación
- Detección automática de tipos MIME
- Manejo de diferentes formatos de respuesta

## Uso

Para utilizar el cliente de Moodle:

```python
from moodle.client import MoodleClient

# Inicializar el cliente
moodle_client = MoodleClient(
    url="http://moodle.example.com",
    token="your_moodle_api_token"
)

# Obtener cursos
courses = moodle_client.get_courses()
for course in courses:
    print(f"Curso: {course['fullname']}")

# Obtener contenido de un curso específico
course_id = 123
contents = moodle_client.get_course_contents(course_id)

# Descargar un archivo
file_url = "http://moodle.example.com/webservice/pluginfile.php/123/mod_resource/content/1/example.pdf"
filename = "example.pdf"
content, content_type = moodle_client.download_file(file_url, filename)
```

## Obtener un token de API de Moodle

Para utilizar este módulo, necesitas un token de API de Moodle. Para obtenerlo:

1. Inicia sesión en tu instancia de Moodle
2. Ve a "Preferencias" en tu perfil
3. Haz clic en "Seguridad" → "Claves de seguridad"
4. Genera un nuevo token para el servicio "Servicios web externos"