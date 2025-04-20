# Guía Rápida: Sistema RAG para Moodle

Esta guía proporciona instrucciones paso a paso para configurar y ejecutar el sistema RAG para Moodle. Este sistema permite descargar documentos de Moodle, indexarlos en una base de datos vectorial (Qdrant) y consultarlos mediante un chat interactivo.

## Requisitos Previos

- Docker y Docker Compose instalados
- Python 3.8 o superior
- Acceso a una instancia de Moodle con un token de API

## Pasos para Ejecutar el Sistema

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd <directorio-del-repositorio>
```

### 2. Iniciar los Servicios con Docker Compose

Este comando iniciará todos los servicios necesarios: Moodle, PostgreSQL, Qdrant y Ollama.

```bash
docker-compose up -d
```

Espera unos minutos hasta que todos los servicios estén en funcionamiento. Puedes verificar el estado con:

```bash
docker-compose ps
```

### 3. Configurar el Entorno

Ejecuta el script de configuración para crear un entorno virtual e instalar las dependencias:

```bash
chmod +x setup.sh
./setup.sh
```

Activa el entorno virtual:

```bash
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 4. Configurar el Token de Moodle

Puedes configurar el token de Moodle de dos formas:

**Opción 1: Variable de entorno**
```bash
export MOODLE_TOKEN=tu_token_de_moodle
```

**Opción 2: Editar config.yaml**
```bash
# Abre el archivo config.yaml y edita la línea:
# token: tu_token_de_moodle
```

### 5. Descargar e Indexar Documentos de Moodle

Este paso descarga los documentos de Moodle y los indexa en Qdrant:

```bash
python main.py --index
# o
./run.sh indexar
# o
make indexar
```

### 6. Consultar los Documentos

Tienes dos opciones para consultar los documentos:

#### Opción A: Chat por Consola

```bash
python main.py --chat
# o
./run.sh chat
# o
make chat
```

#### Opción B: Interfaz Web

```bash
python main.py --web
# o
./run.sh web
# o
make web
```

Luego abre tu navegador en [http://localhost:5000](http://localhost:5000)

## Solución de Problemas Comunes

### Error de Conexión con Moodle

Si ves errores como "No se pudo conectar con Moodle":

1. Verifica que Moodle esté en funcionamiento: `docker-compose ps`
2. Comprueba que el token de Moodle sea válido
3. Asegúrate de que la URL de Moodle sea correcta en config.yaml

### Error de Conexión con Qdrant

Si ves errores relacionados con Qdrant:

1. Verifica que Qdrant esté en funcionamiento: `docker-compose ps`
2. Comprueba la configuración de host y puerto en config.yaml

### Error de Conexión con Ollama

Si ves errores relacionados con Ollama:

1. Verifica que Ollama esté en funcionamiento: `docker-compose ps`
2. Comprueba que el modelo necesario esté descargado:
   ```bash
   curl http://localhost:11434/api/tags
   ```
3. Si el modelo no está descargado, puedes descargarlo con:
   ```bash
   curl -X POST http://localhost:11434/api/pull -d '{"name": "llama3:8b"}'
   ```

### Error de Conexión con PostgreSQL

Si ves errores relacionados con PostgreSQL:

1. Verifica que PostgreSQL esté en funcionamiento: `docker-compose ps`
2. Comprueba la cadena de conexión en config.yaml

## Comandos Útiles

### Ver Ayuda

```bash
make help
# o
python main.py --help
```

### Fine-tuning Local (con Ollama)

```bash
python main.py --fine-tune --provider local
# o
./run.sh fine-tuning
# o
make fine-tuning
```

### Fine-tuning con OpenAI

```bash
python main.py --fine-tune --provider openai
# o
./run.sh fine-tuning-openai
# o
make fine-tuning-openai
```

## Acceso a las Interfaces Web

- **Moodle**: [http://localhost:8080](http://localhost:8080)
  - Usuario: admin
  - Contraseña: admin_pass

- **Ollama Web UI**: [http://localhost:8081](http://localhost:8081)

- **Qdrant**: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

- **Aplicación RAG**: [http://localhost:5000](http://localhost:5000)