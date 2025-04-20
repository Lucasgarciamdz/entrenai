# Instrucciones para crear un workflow en n8n para Moodle

Después de configurar la API de Moodle y obtener el token, sigue estos pasos para crear un workflow en n8n que extraiga el archivo "Archivo_prueba.txt" del curso "Curso_prueba".

## 1. Acceder a n8n

1. Abre un navegador y ve a http://localhost:5678
2. Inicia sesión con:
   - Usuario: admin
   - Contraseña: admin

## 2. Configurar el token de Moodle (escoge UNA de estas opciones)

### Opción A: Importar el workflow pre-configurado (recomendado)
1. En n8n, haz clic en "Workflows" en el menú lateral
2. Haz clic en el botón "Import from file"
3. Selecciona el archivo `workflow_moodle_extraccion.json`
4. **IMPORTANTE**: Edita el nodo "Configuración" y cambia el valor del campo "moodleToken" por el token que obtuviste de Moodle

### Opción B: Usar el archivo de ayuda
1. Monta el archivo `n8n_helpers.js` en el contenedor de n8n:
   ```bash
   docker cp n8n_helpers.js codigo_tesis-n8n-1:/home/node/
   ```
2. Edita el archivo `n8n_helpers.js` y actualiza la propiedad `token` con tu token de Moodle
3. En cualquier nodo "Function" del workflow puedes usar:
   ```javascript
   const helpers = require('/home/node/n8n_helpers.js');
   const moodleConfig = helpers.getMoodleConfig();
   // Ahora puedes usar moodleConfig.token, moodleConfig.url, etc.
   ```

### Opción C: Modificar el docker-compose.n8n.yml
1. Edita el archivo `.env` y añade tu token de Moodle:
   ```
   MOODLE_TOKEN=tu_token_generado
   ```
2. Reinicia el contenedor de n8n:
   ```bash
   docker compose -f docker-compose.n8n.yml down
   docker compose -f docker-compose.n8n.yml up -d
   ```
3. Ahora podrás usar `{{$env.MOODLE_TOKEN}}` en tus nodos

## 3. Crear un workflow desde cero (si no importaste el workflow)

1. Haz clic en "Create new workflow"
2. Asigna un nombre: "Extracción de Archivo Moodle"
3. Haz clic en "Create"

### Paso 1: Crear nodo de configuración
1. Haz clic en el botón "+" para añadir un nuevo nodo
2. Busca y selecciona "Set"
3. Configura el nodo:
   - Nombre: "Configuración"
   - Asigna las siguientes variables:
     - moodleToken: [Pega aquí el token generado]
     - moodleUrl: http://moodle:8080

### Paso 2: Obtener cursos
1. Añade un nodo "HTTP Request" conectado al anterior
2. Configura el nodo:
   - Nombre: "Obtener Cursos"
   - Método: GET
   - URL: `={{ $node["Configuración"].json["moodleUrl"] }}/webservice/rest/server.php`
   - Authentication: None
   - Query Parameters:
     - `wstoken`: `={{ $node["Configuración"].json["moodleToken"] }}`
     - `wsfunction`: `core_course_get_courses`
     - `moodlewsrestformat`: `json`
3. Haz clic en "Execute Node" para probar

### Paso 3: Filtrar curso específico
1. Añade un nuevo nodo "Function" conectado al anterior
2. Configura el nodo:
   - Nombre: "Filtrar Curso Prueba"
   - Función JavaScript:
   ```javascript
   // Si es un array, buscar el curso que contiene "Curso_prueba" en el nombre
   if (Array.isArray(items[0].json)) {
     const cursos = items[0].json;
     const cursoPrueba = cursos.find(curso => curso.fullname.includes('Curso_prueba'));
     
     if (cursoPrueba) {
       return [{ json: { 
         cursoId: cursoPrueba.id,
         moodleToken: $node["Configuración"].json.moodleToken,
         moodleUrl: $node["Configuración"].json.moodleUrl
       } }];
     }
   }
   
   // Si no se encuentra, devolver mensaje de error
   return [{ json: { 
     error: 'Curso no encontrado',
     moodleToken: $node["Configuración"].json.moodleToken,
     moodleUrl: $node["Configuración"].json.moodleUrl
   } }];
   ```
3. Haz clic en "Execute Node" para probar

### Paso 4: Obtener contenido del curso
1. Añade un nuevo nodo "HTTP Request" conectado al anterior
2. Configura el nodo:
   - Nombre: "Obtener Contenido del Curso"
   - Método: GET
   - URL: `={{ $json.moodleUrl }}/webservice/rest/server.php`
   - Authentication: None
   - Query Parameters:
     - `wstoken`: `={{ $json.moodleToken }}`
     - `wsfunction`: `core_course_get_contents`
     - `courseid`: `={{ $json.cursoId }}`
     - `moodlewsrestformat`: `json`
3. Haz clic en "Execute Node" para probar

### Paso 5: Extraer la URL del archivo
1. Añade un nuevo nodo "Function" conectado al anterior
2. Configura el nodo:
   - Nombre: "Extraer URL del Archivo"
   - Función JavaScript:
   ```javascript
   // Procesar el contenido del curso para encontrar el archivo
   const contenidoCurso = items[0].json;
   let archivoEncontrado = null;
   
   // Mantener la configuración para los siguientes nodos
   const config = {
     moodleToken: $node["Configuración"].json.moodleToken,
     moodleUrl: $node["Configuración"].json.moodleUrl
   };
   
   // Recorrer secciones, módulos y buscar el archivo
   for (const seccion of contenidoCurso) {
     if (seccion.modules) {
       for (const modulo of seccion.modules) {
         if (modulo.modname === 'resource' && modulo.contents) {
           for (const contenido of modulo.contents) {
             if (contenido.filename === 'Archivo_prueba.txt') {
               archivoEncontrado = {
                 nombre: contenido.filename,
                 tipo: contenido.mimetype,
                 url: contenido.fileurl,
                 tamano: contenido.filesize,
                 ...config
               };
               break;
             }
           }
         }
       }
     }
   }
   
   if (archivoEncontrado) {
     return [{ json: archivoEncontrado }];
   } else {
     return [{ json: { error: 'Archivo no encontrado', ...config } }];
   }
   ```
3. Haz clic en "Execute Node" para probar

### Paso 6: Descargar el archivo
1. Añade un nuevo nodo "HTTP Request" conectado al anterior
2. Configura el nodo:
   - Nombre: "Descargar Archivo"
   - Método: GET
   - URL: `={{ $json.url }}&token={{ $json.moodleToken }}`
   - Authentication: None
   - Response Format: String
3. Haz clic en "Execute Node" para probar

## 4. Guardar y activar el workflow

1. Haz clic en "Save" para guardar el workflow
2. Activa el workflow con el interruptor en la parte superior derecha

Este workflow básico te permitirá extraer el contenido del archivo "Archivo_prueba.txt" del curso "Curso_prueba". En los siguientes pasos, añadiremos la funcionalidad para procesar este contenido con Qdrant y Ollama.