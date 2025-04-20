# Instrucciones para utilizar Moodle

## Acceso a Moodle
1. Abrir un navegador web y acceder a: http://localhost:8080
2. Iniciar sesión con las siguientes credenciales:
   - **Usuario**: admin
   - **Contraseña**: admin_pass

## Pasos para crear un curso y subir un archivo de prueba
1. Una vez iniciada la sesión, ir al tablero de administración
2. Seleccionar "Administración del sitio" > "Cursos" > "Gestionar cursos y categorías"
3. Crear una nueva categoría si lo desea (opcional)
4. Crear un nuevo curso:
   - Nombre completo: "Curso de Prueba"
   - Nombre corto: "prueba"
   - Completar los demás campos según preferencia
   - Hacer clic en "Guardar y mostrar"
5. En el curso recién creado, activar la edición (botón "Activar edición")
6. Añadir un recurso de tipo "Archivo":
   - Hacer clic en "Añadir una actividad o un recurso"
   - Seleccionar "Archivo" 
   - Completar nombre y descripción
   - Arrastrar o subir un archivo TXT de prueba
   - Guardar cambios

## Notas importantes
- La instalación de Moodle puede tardar unos minutos en completarse.
- El ID del curso será necesario para el siguiente paso (integración con n8n).
- Para verificar que todo funciona correctamente, asegúrese de poder descargar el archivo subido.

## Próximos pasos
Una vez que haya creado el curso y subido un archivo, podremos continuar con:
1. Configuración de n8n para conectarse con Moodle
2. Creación del workflow para extraer y procesar el archivo
3. Integración con Qdrant y Ollama para el procesamiento avanzado