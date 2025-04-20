# Instrucciones para habilitar la API de Moodle y obtener token

Para que n8n pueda comunicarse con Moodle, necesitamos habilitar los servicios web de Moodle y generar un token de API. Sigue estos pasos:

## 1. Habilitar servicios web en Moodle

1. Inicia sesión en Moodle como administrador (admin/admin_pass)
2. Ve a "Administración del sitio" > "Características avanzadas"
3. Marca la casilla "Habilitar servicios web" y guarda los cambios
4. Ve a "Administración del sitio" > "Plugins" > "Servicios web" > "Protocolos externos"
5. Habilita el protocolo "REST" (activa la casilla correspondiente)
6. Guarda los cambios

## 2. Crear un servicio personalizado

1. Ve a "Administración del sitio" > "Plugins" > "Servicios web" > "Servicios externos"
2. Haz clic en "Agregar"
3. Completa el formulario:
   - Nombre: "API para n8n"
   - Habilitado: Activado
   - Solo para usuarios autorizados: Activado
4. Guarda los cambios

## 3. Agregar funciones al servicio

1. Después de crear el servicio, haz clic en "Agregar funciones" en la fila correspondiente
2. Busca y añade las siguientes funciones:
   - `core_course_get_courses`
   - `core_course_get_contents`
   - `core_files_get_files`
   - `mod_resource_get_resources_by_courses`
3. Guarda los cambios

## 4. Crear un usuario para el servicio web

1. Ve a "Administración del sitio" > "Usuarios" > "Cuentas" > "Agregar un usuario"
2. Completa la información del usuario:
   - Nombre de usuario: api_user
   - Contraseña: Api123456#
   - Nombre completo: API User
   - Correo electrónico: api@example.com
3. Guarda los cambios

## 5. Autorizar al usuario para el servicio

1. Ve a "Administración del sitio" > "Plugins" > "Servicios web" > "Servicios externos"
2. Haz clic en "Usuarios autorizados" en la fila de "API para n8n"
3. Busca y agrega al usuario "api_user"
4. Guarda los cambios

## 6. Generar un token para el usuario

1. Ve a "Administración del sitio" > "Plugins" > "Servicios web" > "Tokens"
2. Haz clic en "Crear token"
3. Completa el formulario:
   - Usuario: api_user
   - Servicio: API para n8n
   - Válido hasta: (opcional) dejar en blanco para que no expire
4. Haz clic en "Guardar cambios"
5. **IMPORTANTE**: Copia el token generado y guárdalo en un lugar seguro

## 7. Actualizar el archivo .env

1. Abre el archivo `.env` en el directorio raíz del proyecto
2. Actualiza la variable `MOODLE_TOKEN` con el token generado:
   ```
   MOODLE_TOKEN=tu_token_generado
   ```
3. Guarda el archivo

Una vez completados estos pasos, n8n podrá comunicarse con Moodle utilizando el token generado.

ver si el usuario tiene permisos para acceder a los cursos
Update course settings
moodle/course:update
View hidden courses
moodle/course:viewhiddencourses
View courses without participation
moodle/course:view
