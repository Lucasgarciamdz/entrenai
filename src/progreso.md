# Progreso del Proyecto RAG para Moodle

## 20-Abril-2025: Pruebas iniciales de ingestión de datos

### Configuración inicial
- Verificamos que los contenedores Docker están corriendo correctamente:
  - Moodle, MariaDB, Postgres, Qdrant, Ollama y Ollama-webui están en funcionamiento
- Verificamos la existencia del token de Moodle en las variables de entorno:
  - Token encontrado: `MOODLE_TOKEN=ea2972a640e9c50404e9c6c20df9b362`

### Primer intento de ingestión
- Ejecutamos: `python main.py --index`
- **Problema detectado**: Error de resolución de nombre 'moodle'
  ```
  Error al comunicarse con Moodle: HTTPConnectionPool(host='moodle', port=8080): 
  Max retries exceeded with url: /webservice/rest/server.php 
  (Caused by NameResolutionError: Failed to resolve 'moodle' ([Errno 8] nodename nor servname provided, or not known))
  ```
- **Análisis del problema**: La aplicación intenta conectarse a un host llamado 'moodle', pero este nombre no se puede resolver en el sistema local. En el archivo `config.yaml` la URL está configurada como "http://moodle:8080", lo que funciona dentro de la red Docker pero no desde la máquina host.

### Solución propuesta
- Modificamos el archivo `config.yaml` para cambiar la URL de Moodle de "http://moodle:8080" a "http://localhost:8080".
- Sin embargo, el error persiste. Revisando el código en profundidad, identificamos que aunque hemos cambiado la configuración, el error sigue ocurriendo con el mismo host.
- **Análisis adicional**: Es posible que la aplicación esté cachéando la configuración o que haya algún problema adicional en la implementación del cliente de Moodle.

### Revisión del código
- Al revisar `main.py` y `moodle/client.py`, encontramos que la URL se pasa correctamente desde la configuración al cliente de Moodle.
- Sin embargo, el error sigue mostrando que intenta resolver "moodle" en lugar de "localhost".
- Necesitamos revisar la función `_make_request` y la cadena de llamadas para entender por qué sigue usando el nombre de host "moodle" a pesar de que la configuración ha cambiado.

### Identificación de la causa raíz
- Verificamos la configuración real cargada en tiempo de ejecución:
  ```
  python -c "from core.config import load_config; from pathlib import Path; print(load_config(Path('config.yaml')))"
  ```
- **Problema encontrado**: A pesar de que el archivo `config.yaml` tiene la URL correcta (http://localhost:8080), la configuración cargada muestra `'url': 'http://moodle:8080'`.
- Revisando `core/config.py`, descubrimos que las variables de entorno tienen prioridad sobre la configuración en el archivo YAML.
- La variable `MOODLE_URL` está establecida en el entorno como "http://moodle:8080", lo que provoca que ignore la configuración en el archivo.

### Segunda solución propuesta
- Probamos quitando la variable de entorno MOODLE_URL:
  ```
  unset MOODLE_URL && python -c "from core.config import load_config; from pathlib import Path; print(load_config(Path('config.yaml')))"
  ```
- Ahora la configuración cargada tiene la URL correcta: `'url': 'http://localhost:8080'`
- Sin embargo, al verificar las variables de entorno, encontramos que no había una variable MOODLE_URL configurada explícitamente:
  ```
  env | grep MOODLE
  MOODLE_TOKEN=ea2972a640e9c50404e9c6c20df9b362
  MOODLE_HOST_URL=http://localhost:8080
  ```
- Esto sugiere que hay otro problema en la implementación del sistema de configuración o posiblemente en cómo se inicializan las variables.

### Tercer intento de ingestión
- Ejecutamos nuevamente: `python main.py --index`
- **Progreso**: Ahora la conexión alcanza el servidor Moodle correctamente, pero obtenemos un error de autenticación:
  ```
  Error al comunicarse con Moodle: 403 Client Error: Forbidden for url: 
  http://localhost:8080/webservice/rest/server.php?wstoken=ea2972a640e9c50404e9c6c20df9b362&wsfunction=core_enrol_get_users_courses&moodlewsrestformat=json
  ```
- **Análisis del error**: El error 403 (Forbidden) indica que el token de Moodle no es válido o no tiene los permisos necesarios para acceder a la API.

### Verificación del token de Moodle
- Intentamos verificar el token con una petición directa al servidor Moodle:
  ```
  curl -v "http://localhost:8080/webservice/rest/server.php?wstoken=ea2972a640e9c50404e9c6c20df9b362&wsfunction=core_webservice_get_site_info&moodlewsrestformat=json"
  ```
- **Resultado**: Recibimos una respuesta HTTP 403 Forbidden, lo que confirma que el token no es válido o no tiene los permisos correctos.
  ```
  < HTTP/1.0 403 Forbidden
  < Date: Sun, 20 Apr 2025 16:17:03 GMT
  < Server: Apache
  < Content-Length: 0
  < Connection: close
  < Content-Type: text/html; charset=utf-8
  ```

### Corrección del token
- Actualizamos el token de Moodle en el archivo de configuración:
  ```yaml
  moodle:
    url: "http://localhost:8080"
    token: "cd61497cb1674e47de537ec0a0c9c5da"
    target_course: "prueba"
  ```
- Configuramos la variable de entorno con el nuevo token:
  ```bash
  export MOODLE_TOKEN=cd61497cb1674e47de537ec0a0c9c5da
  ```
- Sin embargo, al verificar la conexión con el nuevo token, seguimos recibiendo errores de autenticación:
  ```
  Error de Moodle: Invalid token - token not found
  ```

### Análisis de la instancia de Moodle
- Verificamos que la instancia de Moodle está funcionando correctamente:
  ```
  curl http://localhost:8080
  ```
- La respuesta muestra que Moodle está en funcionamiento y tiene un curso llamado "Curso_prueba".
- Al intentar acceder al curso, recibimos una redirección a la página de login:
  ```
  curl -v "http://localhost:8080/course/view.php?id=2"
  ```
  ```
  < HTTP/1.1 303 See Other
  < Location: http://localhost:8080/login/index.php
  ```
- Esto confirma que la instancia está funcionando pero requiere autenticación para acceder a los contenidos.

### Configuración actual
- Verificamos la configuración actual cargada:
  ```
  python -c "from core.config import load_config; from pathlib import Path; config = load_config(Path('config.yaml')); print(config['moodle']['url'], config['moodle']['token'], config['moodle']['target_course'])"
  ```
- Confirmamos que los valores son:
  ```
  http://localhost:8080 cd61497cb1674e47de537ec0a0c9c5da prueba
  ```

### Problema con Qdrant
- Al intentar ejecutar la ingestión con un token válido (a247db8dff921708bc2e00f16f0b7ac5), encontramos un nuevo error:
  ```
  Not found: Collection `moodle_docs` doesn't exist!
  ```
- **Análisis del problema**: La clase `VectorStore` intenta usar una colección en Qdrant que aún no ha sido creada.

### Solución implementada
- Modificamos la clase `VectorStore` en `rag/vector_store.py` para que verifique si la colección existe y la cree automáticamente si no:
  1. Añadimos un método `_create_collection_if_not_exists()` que verifica si la colección existe
  2. Si la colección no existe, la crea con el tamaño de vector adecuado y la métrica de distancia coseno
  3. Llamamos a este método desde el constructor de la clase y antes de cada operación que requiera la colección
  4. Actualizamos la función de búsqueda para también verificar la existencia de la colección

### Cuarto intento de ingestión
- Ejecutamos nuevamente: `python main.py --index`
- **Progreso parcial**: Ahora el sistema puede:
  1. Conectarse correctamente a Moodle con el token correcto
  2. Descargar los documentos del curso
  3. Crear la colección en Qdrant automáticamente
- **Nuevo problema**: Al intentar indexar los documentos en Qdrant, recibimos un error de espacio en disco:
  ```
  Error al indexar documento en Qdrant: Unexpected Response: 500 (Internal Server Error)
  Raw response content:
  b'{"status":{"error":"Service internal error: No space left on device: WAL buffer size exceeds available disk space"},"time":0.043654541}'
  ```
- **Análisis del error**: El contenedor Docker de Qdrant no tiene suficiente espacio en disco para almacenar los vectores.

### Próximos pasos
1. Resolver el problema de espacio en disco de Qdrant:
   - Liberar espacio en el sistema host
   - Modificar la configuración de Docker Compose para asignar más espacio al volumen de Qdrant
   - Alternativamente, considerar reducir el tamaño de los documentos o guardar solo parte de ellos para la prueba de concepto
2. Una vez resuelto el problema de espacio, volver a probar la ingestión completa
3. Después de una ingestión exitosa, probar la funcionalidad de búsqueda y chat
