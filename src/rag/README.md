# Módulo RAG (Recuperación Aumentada por Generación)

Este módulo implementa la funcionalidad central de Recuperación Aumentada por Generación (RAG) del sistema.

## Propósito

El módulo `rag` proporciona las herramientas necesarias para:

1. Procesar diferentes tipos de documentos y extraer su texto
2. Generar embeddings (representaciones vectoriales) de los documentos
3. Almacenar y recuperar estos embeddings de una base de datos vectorial (Qdrant)
4. Reordenar los resultados de búsqueda para mejorar la relevancia

## Componentes

### document_processor.py

Este archivo contiene la clase `DocumentProcessor` que se encarga de extraer texto de diferentes tipos de documentos:

- PDF (usando PyPDF2)
- Presentaciones PowerPoint (usando python-pptx)
- Documentos Word (usando python-docx)
- Imágenes (usando OCR con pytesseract)
- Archivos de texto plano

El procesador detecta automáticamente el tipo de documento basándose en el tipo MIME y aplica el método de extracción adecuado.

### vector_store.py

Este archivo implementa la clase `VectorStore` que proporciona una interfaz para:

- Generar embeddings de texto usando diferentes proveedores:
  - Ollama (local)
  - OpenAI
- Almacenar documentos y sus embeddings en Qdrant
- Realizar búsquedas semánticas por similitud

### reranking.py

Proporciona funciones para reordenar los resultados de búsqueda basándose en criterios adicionales, mejorando la relevancia de los resultados devueltos al usuario.

## Uso

### Procesamiento de documentos

```python
from rag.document_processor import DocumentProcessor

# Inicializar el procesador
processor = DocumentProcessor()

# Procesar un documento
content = b'contenido binario del documento'
content_type = 'application/pdf'
filename = 'documento.pdf'

text, metadata = processor.process_document(content, content_type, filename)
print(f"Texto extraído: {text[:100]}...")
```

### Almacenamiento y búsqueda vectorial

```python
from rag.vector_store import VectorStore

# Inicializar con Ollama (local)
vector_store = VectorStore(
    host="localhost",
    port=6333,
    collection_name="documentos",
    embedding_provider="ollama",
    ollama_url="http://localhost:11434"
)

# O inicializar con OpenAI
vector_store = VectorStore(
    host="localhost",
    port=6333,
    collection_name="documentos",
    embedding_provider="openai",
    openai_api_key="tu_api_key"
)

# Indexar un documento
vector_store.index_document(
    texto="Contenido del documento para indexar",
    metadata={"filename": "documento.pdf", "curso": "Matemáticas"}
)

# Buscar documentos similares
resultados = vector_store.search("consulta del usuario", limit=5)
for r in resultados:
    print(f"Score: {r['score']}, Texto: {r['chunk_text']}")
```

### Reordenamiento de resultados

```python
from rag.reranking import rerank_fragments

# Reordenar fragmentos por relevancia
fragmentos = ["texto1", "texto2", "texto3"]
pregunta = "¿Cuál es la fórmula de la energía?"
fragmentos_ordenados = rerank_fragments(pregunta, fragmentos)
```