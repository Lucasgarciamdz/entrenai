# Sistema RAG para Moodle

Este proyecto implementa un sistema de Recuperación Aumentada por Generación (RAG) para consultar documentos almacenados en Moodle, permitiendo a los estudiantes acceder a información relevante de sus cursos mediante un chat interactivo.

## Características

- Descarga automática de documentos desde Moodle
- Procesamiento de múltiples tipos de documentos:
  - Archivos PDF
  - Presentaciones PowerPoint
  - Documentos Word
  - Imágenes (con OCR)
  - Archivos de texto plano
- Indexación de documentos en Qdrant (base de datos vectorial)
- Soporte para múltiples proveedores de embeddings:
  - Ollama (local)
  - OpenAI
- Chat interactivo con memoria de conversaciones
- Interfaz web para consultar documentos
- Fine-tuning de modelos con datos de conversaciones
- Compatible con el stack de Docker existente

## Requisitos

- Python 3.8+
- Docker y Docker Compose para los servicios externos:
  - Moodle
  - PostgreSQL
  - Qdrant
  - Ollama

## Instalación

1. Clona este repositorio:
```bash
git clone <url-del-repositorio>
cd <directorio-del-repositorio>
```

2. Crea y activa un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias (el script setup.sh lo hace automáticamente):
```bash
# Opción 1: Usar el script de instalación
chmod +x setup.sh
./setup.sh

# Opción 2: Instalación manual
pip install -r requirements.txt
```

4. Inicia los servicios con Docker Compose:
```bash
docker-compose up -d
```

5. Configura el token de Moodle:
```bash
# Puedes configurarlo como variable de entorno
export MOODLE_TOKEN=tu_token_de_moodle

# O editarlo directamente en config.yaml
```

## Uso

### Indexar documentos de Moodle

Para descargar e indexar documentos de Moodle:

```bash
python main.py --index
```

El sistema detectará automáticamente el tipo de archivo y extraerá el texto utilizando el procesador adecuado:
- PDF: Extracción de texto con PyPDF2
- PowerPoint: Extracción de texto de diapositivas con python-pptx
- Word: Extracción de texto con python-docx
- Imágenes: OCR con pytesseract
- Texto plano: Procesamiento directo

### Iniciar el chat interactivo (consola)

Para interactuar con el sistema desde la consola:

```bash
python main.py --chat
```

### Iniciar la aplicación web

Para iniciar la interfaz web:

```bash
python main.py --web
```

Luego abre tu navegador en [http://localhost:5000](http://localhost:5000)

### Fine-tuning del modelo

Para realizar fine-tuning del modelo con los datos de las conversaciones:

```bash
# Fine-tuning local (con Ollama)
python main.py --fine-tune --provider local

# Fine-tuning con OpenAI
python main.py --fine-tune --provider openai
```

El proceso de fine-tuning:
1. Extrae las conversaciones de la base de datos
2. Prepara los datos en el formato adecuado
3. Para fine-tuning local: Genera un archivo JSON y muestra instrucciones para usar Ollama
4. Para OpenAI: Inicia un trabajo de fine-tuning en la plataforma de OpenAI

## Configuración

La configuración se puede realizar a través de variables de entorno o de un archivo `config.yaml`. Las principales opciones son:

### Moodle
- `MOODLE_URL`: URL de la instancia de Moodle (por defecto: http://moodle:8080)
- `MOODLE_TOKEN`: Token de API de Moodle
- `MOODLE_TARGET_COURSE`: Nombre corto del curso objetivo (por defecto: "prueba")

### Qdrant (Base de datos vectorial)
- `QDRANT_HOST`: Host de Qdrant (por defecto: localhost)
- `QDRANT_PORT`: Puerto de Qdrant (por defecto: 6333)
- `QDRANT_COLLECTION`: Nombre de la colección (por defecto: moodle_docs)

### Embeddings
- `EMBEDDING_PROVIDER`: Proveedor de embeddings a utilizar ("ollama" o "openai", por defecto: "ollama")
- `OPENAI_API_KEY`: Clave API de OpenAI (requerida si EMBEDDING_PROVIDER="openai")
- `OPENAI_EMBEDDING_MODEL`: Modelo de embeddings de OpenAI (por defecto: "text-embedding-3-small")

### Ollama
- `OLLAMA_URL`: URL del servidor Ollama (por defecto: http://localhost:11434)
- `OLLAMA_MODEL`: Modelo a utilizar (por defecto: llama3:8b)

### Base de datos
- `POSTGRES_CONNECTION`: Cadena de conexión PostgreSQL (por defecto: postgresql://n8n:n8n_password@localhost:5432/n8n)

## Ejemplo de flujo completo

### 1. Indexar documentos de Moodle

```bash
make indexar
# o
./run.sh indexar
```

### 2. Consultar por chat (consola)

```bash
make chat
# o
./run.sh chat
```

### 3. Fine-tuning local (usando datos de conversaciones)

```bash
make fine-tuning
# o
./run.sh fine-tuning
```

## Scripts de automatización

- `run.sh`: Script simple para ejecutar tareas comunes (indexar, chat, fine-tuning)
- `Makefile`: Comandos rápidos con `make`

## Estructura del Proyecto

El proyecto está organizado en módulos para facilitar su mantenimiento y extensión:

- `main.py`: Punto de entrada principal para todas las funcionalidades

### Módulos

- **core**: Funcionalidades centrales del sistema
  - `core/config.py`: Gestión de configuración
  - `core/errors.py`: Manejo de errores personalizados
  - `core/utils.py`: Utilidades generales y configuración de logging

- **moodle**: Interacción con la plataforma Moodle
  - `moodle/client.py`: Cliente para interactuar con la API de Moodle

- **rag**: Recuperación Aumentada por Generación
  - `rag/document_processor.py`: Procesador de diferentes tipos de documentos (PDF, PPTX, DOCX, imágenes)
  - `rag/vector_store.py`: Wrapper para la interacción con Qdrant y generación de embeddings
  - `rag/reranking.py`: Reranking simple para mejorar la recuperación

- **chat**: Gestión de conversaciones
  - `chat/manager.py`: Gestor de chat con memoria persistente
  - `chat/prompts.py`: Plantillas de prompts reutilizables (en español)

- **web**: Interfaz web
  - `web/app.py`: Aplicación web con Flask

- **fine_tuning**: Herramientas para fine-tuning
  - `fine_tuning/manager.py`: Herramienta para fine-tuning de modelos con datos de conversaciones

## Obtener token de Moodle

Para obtener un token de API de Moodle, sigue estos pasos:

1. Inicia sesión en tu instancia de Moodle
2. Ve a "Preferencias" en tu perfil
3. Haz clic en "Seguridad" → "Claves de seguridad"
4. Genera un nuevo token para el servicio "Servicios web externos"

## Integración con Moodle

Para integrar esta aplicación directamente en Moodle, considere:

1. **Plugin de Moodle**: Crear un plugin personalizado que incorpore la funcionalidad de chat.
2. **iFrame**: Incrustar la aplicación web en un iframe dentro de Moodle.
3. **SSO**: Implementar inicio de sesión único entre Moodle y la aplicación.

## Solución de problemas

### Errores comunes

- **No se puede conectar con Moodle**: Verifica la URL y el token de API en config.yaml
- **No se puede conectar con Qdrant**: Asegúrate de que el servicio de Qdrant esté activo
- **Error en procesamiento de documentos**: Verifica que todas las dependencias estén instaladas
- **Error al generar embeddings**: Comprueba la URL de Ollama o la API Key de OpenAI

## Contribuir

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Haz fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/amazing-feature`)
3. Haz commit de tus cambios (`git commit -m 'Add some amazing feature'`)
4. Haz push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request 
