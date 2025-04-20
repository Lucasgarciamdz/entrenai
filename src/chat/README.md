# Módulo Chat

Este módulo implementa la funcionalidad de chat interactivo del sistema RAG para Moodle.

## Propósito

El módulo `chat` proporciona las herramientas necesarias para:

1. Gestionar conversaciones con el usuario
2. Almacenar el historial de mensajes en una base de datos
3. Generar respuestas utilizando el sistema RAG
4. Proporcionar plantillas de prompts para diferentes escenarios

## Componentes

### manager.py

Este archivo contiene la clase `ChatManager` que se encarga de:

- Crear y gestionar sesiones de chat
- Almacenar mensajes en PostgreSQL
- Recuperar el historial de conversaciones
- Generar respuestas utilizando el sistema RAG
- Proporcionar una interfaz de chat interactiva por consola

La clase `ChatManager` utiliza el componente `VectorStore` del módulo `rag` para buscar información relevante y generar respuestas contextuales.

### prompts.py

Este archivo contiene plantillas de prompts en español para diferentes escenarios:

- `PROMPT_BUSQUEDA`: Para generar respuestas basadas en fragmentos de documentos
- `PROMPT_CHAT`: Para generar respuestas considerando el historial de la conversación
- `PROMPT_RERANKING`: Para reordenar resultados de búsqueda

## Uso

### Iniciar un chat interactivo

```python
from chat.manager import ChatManager
from rag.vector_store import VectorStore

# Inicializar VectorStore
vector_store = VectorStore(
    host="localhost",
    port=6333,
    collection_name="documentos",
    embedding_provider="ollama",
    ollama_url="http://localhost:11434"
)

# Inicializar ChatManager
chat_manager = ChatManager(
    qdrant_client=vector_store,
    db_connection="postgresql://usuario:contraseña@localhost:5432/basededatos",
    ollama_url="http://localhost:11434",
    model_name="llama3:8b"
)

# Iniciar chat interactivo en consola
chat_manager.start_interactive_chat()
```

### Gestionar sesiones y mensajes programáticamente

```python
# Crear una nueva sesión
session_id = chat_manager.create_session()

# Añadir un mensaje del usuario
chat_manager.add_message(session_id, "user", "¿Cuál es la fórmula de la energía?")

# Generar una respuesta
respuesta = chat_manager.generate_response(session_id, "¿Cuál es la fórmula de la energía?")
print(f"Respuesta: {respuesta}")

# Obtener el historial de la conversación
historial = chat_manager.get_history(session_id)
for mensaje in historial:
    print(f"{mensaje['sender']}: {mensaje['content']}")

# Obtener todas las sesiones
sesiones = chat_manager.get_sessions()
for sesion in sesiones:
    print(f"Sesión: {sesion['id']}, Creada: {sesion['created_at']}")
```

### Utilizar plantillas de prompts

```python
from chat.prompts import PROMPT_BUSQUEDA, PROMPT_CHAT

# Utilizar plantilla para búsqueda
prompt_busqueda = PROMPT_BUSQUEDA.format(
    pregunta="¿Cuál es la fórmula de la energía?",
    contexto="La fórmula de la energía es E=mc²"
)

# Utilizar plantilla para chat
prompt_chat = PROMPT_CHAT.format(
    historial="Usuario: Hola\nAsistente: Hola, ¿en qué puedo ayudarte?",
    pregunta="¿Cuál es la fórmula de la energía?"
)
```