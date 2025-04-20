# Instrucciones para implementar el Workflow RAG en n8n

Este documento describe cómo implementar y probar el workflow de Recuperación Aumentada por Generación (RAG) en n8n que procesa archivos de Moodle, los vectoriza y almacena en Qdrant.

## Prerrequisitos

Antes de comenzar, asegúrate de que:

1. Los servicios de Docker están funcionando:
   - Moodle (puerto 8080)
   - n8n (puerto 5678)
   - Qdrant (puerto 6333)
   - Ollama (puerto 11434)

2. Has creado un curso en Moodle con un archivo de texto en la sección "archivos"

3. Tienes un token de API válido de Moodle

## 1. Importar el workflow RAG

1. Accede a n8n en http://localhost:5678
2. Inicia sesión con tus credenciales
3. Ve a "Workflows" en el menú lateral
4. Haz clic en "Import from file"
5. Selecciona el archivo `workflowFinal_rag.json`
6. Haz clic en "Import"

## 2. Configurar la colección de Qdrant

Ejecuta el siguiente comando para crear la colección en Qdrant:

```bash
curl -X PUT http://localhost:6333/collections/moodle_docs -H 'Content-Type: application/json' -d '{"vectors": {"size": 1536, "distance": "Cosine"}}'
```

Verifica que la colección se ha creado correctamente:

```bash
curl http://localhost:6333/collections
```

## 3. Configurar el modelo de Ollama

Asegúrate de tener un modelo compatible con generación de embeddings instalado en Ollama:

```bash
docker exec -it codigo_tesis-ollama-1 ollama pull llama3
```

## 4. Configurar el token de Moodle

En el nodo "Configuración" del workflow, actualiza el valor de `moodleToken` con tu token de API de Moodle.

## 5. Ejecutar el workflow

1. Haz clic en "Save" para guardar el workflow
2. Haz clic en "Execute Workflow" para ejecutarlo

## 6. Verificar resultados

1. **Verificar el procesamiento de contenido:**
   - Revisa el output del nodo "Procesar Contenido" para confirmar que el texto se ha dividido correctamente en chunks

2. **Verificar la generación de embeddings:**
   - Revisa el output del nodo "Generar Embeddings" para confirmar que se han generado vectores

3. **Verificar el almacenamiento en Qdrant:**
   - Consulta Qdrant para verificar que los documentos se han almacenado:

   ```bash
   curl http://localhost:6333/collections/moodle_docs/points/count
   ```

## 7. Solución de problemas comunes

### Error en la generación de embeddings
- Verifica que Ollama esté funcionando: `docker ps | grep ollama`
- Confirma que el modelo está disponible: `docker exec -it codigo_tesis-ollama-1 ollama list`
- Prueba con un modelo alternativo modificando el parámetro en el nodo "Generar Embeddings"

### Error al guardar en Qdrant
- Verifica que Qdrant esté funcionando: `docker ps | grep qdrant`
- Confirma que la colección existe: `curl http://localhost:6333/collections`
- Revisa el formato del payload en el nodo "Preparar Datos Qdrant"

### Errores de conexión a Moodle
- Verifica que Moodle esté funcionando: `docker ps | grep moodle`
- Confirma que el token es válido intentando una petición directa:
  ```bash
  curl "http://localhost:8080/webservice/rest/server.php?wstoken=TUTOKEN&wsfunction=core_course_get_courses&moodlewsrestformat=json"
  ```

## 8. Próximos pasos

Una vez que el workflow funcione correctamente y estés almacenando documentos en Qdrant, puedes:

1. Crear un workflow de consulta que permita hacer preguntas sobre el contenido
2. Implementar una interfaz web para interactuar con el sistema
3. Extender el sistema para procesar otros tipos de archivos (PDF, DOCX, etc.)

## Recursos adicionales

- [Documentación de n8n](https://docs.n8n.io/)
- [Documentación de Qdrant](https://qdrant.tech/documentation/)
- [Documentación de Ollama](https://github.com/ollama/ollama)
- [Moodle Web Services API](https://docs.moodle.org/dev/Web_service_API_functions) 