# Proyecto de RAG para Moodle

Este proyecto proporciona una solución para interactuar con documentos almacenados en Moodle utilizando técnicas de Recuperación Aumentada por Generación (RAG).

## Comparación con N8n

El proyecto ofrece una alternativa más modular y programática al flujo de trabajo original implementado en N8n:

| Característica | Implementación N8n | Implementación Python |
|----------------|-------------------|----------------------|
| Extracción de Moodle | Nodos HTTP y Code | Cliente Python con API dedicada |
| Vectorización | Bloque de Ollama | Integración directa con Ollama API |
| Almacenamiento | Qdrant Node | Cliente Python de Qdrant |
| Interfaz de chat | Integrada en N8n | Consola interactiva y app web |
| Memoria | Limitada | Persistente en PostgreSQL |
| Extensibilidad | Mediante flujos | Código Python modular |

## Estructura del Proyecto

- `docker-compose.yml`: Configuración de los servicios Docker
- `Workflow_definitivo.json`: Flujo de trabajo original en N8n
- `src/`: Implementación en Python
  - Ver el [README específico](src/README.md) para más detalles

## Requisitos

- Docker y Docker Compose
- Python 3.8+

## Instalación Rápida

Inicia los servicios requeridos:

```bash
docker-compose up -d
```

Configura el entorno Python:

```bash
cd src
./setup.sh  # En Windows: setup.bat
```

## Uso

Ver las [instrucciones detalladas](src/README.md) en el directorio `src`.

## Próximos Pasos

- Integrar el sistema como plugin de Moodle
- Mejorar la interfaz web
- Añadir soporte para más tipos de archivos (PDF, DOCX)
- Implementar autenticación y autorización 