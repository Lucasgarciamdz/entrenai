"""
Gestor de chat con memoria de conversaciones y RAG.
"""
import requests
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
import uuid
from core.utils import configurar_logging
from core.errors import ErrorChat
from rag.vector_store import VectorStore
from rag.reranking import rerank_fragments
from chat.prompts import PROMPT_CHAT

class ChatManager:
    """
    Gestor de chat con memoria de conversaciones y RAG
    """
    def __init__(self, qdrant_client: VectorStore, db_connection: str, ollama_url: str, model_name: str = "llama3:8b"):
        """
        Inicializa el gestor de chat.
        
        Args:
            qdrant_client: Cliente de Qdrant para búsqueda vectorial
            db_connection: Cadena de conexión a PostgreSQL
            ollama_url: URL de Ollama para LLM
            model_name: Nombre del modelo de Ollama
        """
        self.qdrant = qdrant_client
        self.db_connection = db_connection
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.logger = configurar_logging("chat_manager")
        self._init_db()

    def _init_db(self):
        """
        Inicializa las tablas de la base de datos si no existen.
        
        Raises:
            ErrorChat: Si ocurre un error al inicializar la base de datos
        """
        try:
            with psycopg2.connect(self.db_connection) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS chat_sessions (
                            id VARCHAR(36) PRIMARY KEY,
                            created_at TIMESTAMP NOT NULL,
                            updated_at TIMESTAMP NOT NULL
                        )
                    """)
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS chat_messages (
                            id VARCHAR(36) PRIMARY KEY,
                            session_id VARCHAR(36) REFERENCES chat_sessions(id),
                            sender VARCHAR(16) NOT NULL,
                            content TEXT NOT NULL,
                            timestamp TIMESTAMP NOT NULL
                        )
                    """)
        except Exception as e:
            self.logger.error(f"Error al inicializar la base de datos de chat: {e}")
            raise ErrorChat(str(e))

    def create_session(self) -> Optional[str]:
        """
        Crea una nueva sesión de chat.
        
        Returns:
            ID de la sesión creada o None si ocurre un error
        """
        try:
            session_id = str(uuid.uuid4())
            now = datetime.now()
            with psycopg2.connect(self.db_connection) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO chat_sessions (id, created_at, updated_at) VALUES (%s, %s, %s)",
                        (session_id, now, now)
                    )
            return session_id
        except Exception as e:
            self.logger.error(f"Error al crear sesión de chat: {e}")
            return None

    def add_message(self, session_id: str, sender: str, content: str):
        """
        Añade un mensaje a una sesión de chat.
        
        Args:
            session_id: ID de la sesión
            sender: Remitente del mensaje ('user' o 'assistant')
            content: Contenido del mensaje
            
        Raises:
            ErrorChat: Si ocurre un error al guardar el mensaje
        """
        try:
            msg_id = str(uuid.uuid4())
            now = datetime.now()
            with psycopg2.connect(self.db_connection) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO chat_messages (id, session_id, sender, content, timestamp) VALUES (%s, %s, %s, %s, %s)",
                        (msg_id, session_id, sender, content, now)
                    )
                    cur.execute(
                        "UPDATE chat_sessions SET updated_at = %s WHERE id = %s",
                        (now, session_id)
                    )
        except Exception as e:
            self.logger.error(f"Error al guardar mensaje de chat: {e}")
            raise ErrorChat(str(e))

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de mensajes de una sesión.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Lista de mensajes con remitente, contenido y timestamp
        """
        try:
            with psycopg2.connect(self.db_connection) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(
                        "SELECT sender, content, timestamp FROM chat_messages WHERE session_id = %s ORDER BY timestamp ASC",
                        (session_id,)
                    )
                    return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            self.logger.error(f"Error al obtener historial de chat: {e}")
            return []

    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene los mensajes de una sesión en formato para la interfaz web.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Lista de mensajes con role y content
        """
        try:
            with psycopg2.connect(self.db_connection) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(
                        "SELECT sender, content FROM chat_messages WHERE session_id = %s ORDER BY timestamp ASC",
                        (session_id,)
                    )
                    return [{"role": row["sender"], "content": row["content"]} for row in cur.fetchall()]
        except Exception as e:
            self.logger.error(f"Error al obtener mensajes de sesión: {e}")
            return []

    def generate_response(self, session_id: str, pregunta: str) -> str:
        """
        Genera una respuesta a la pregunta del usuario utilizando RAG.
        
        Args:
            session_id: ID de la sesión
            pregunta: Pregunta del usuario
            
        Returns:
            Respuesta generada
        """
        try:
            resultados = self.qdrant.search(pregunta, limit=5)
            fragmentos = [r.get('chunk_text', '') for r in resultados]
            fragmentos_ordenados = rerank_fragments(pregunta, fragmentos)
            contexto = '\n'.join(fragmentos_ordenados[:3])
            historial = self.get_history(session_id)
            historial_texto = '\n'.join([
                f"{m['sender']}: {m['content']}" for m in historial
            ])
            prompt = PROMPT_CHAT.format(historial=historial_texto, pregunta=pregunta)
            respuesta = self._call_llm(prompt, contexto)
            self.add_message(session_id, "user", pregunta)
            self.add_message(session_id, "assistant", respuesta)
            return respuesta
        except Exception as e:
            self.logger.error(f"Error al generar respuesta: {e}")
            error_message = "Lo siento, no pude generar una respuesta en este momento."
            self.add_message(session_id, "assistant", error_message)
            return error_message

    def _call_llm(self, prompt: str, contexto: str) -> str:
        """
        Llama al modelo de lenguaje para generar una respuesta.
        
        Args:
            prompt: Prompt para el modelo
            contexto: Contexto relevante para la respuesta
            
        Returns:
            Respuesta generada por el modelo
        """
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": f"{prompt}\n\nContexto relevante:\n{contexto}",
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except Exception as e:
            self.logger.error(f"Error al llamar al LLM: {e}")
            return ""

    def start_interactive_chat(self):
        """
        Inicia un chat interactivo en la consola.
        """
        print("¡Bienvenido al chat de consulta de documentos de Moodle!")
        print("Escribe 'salir' para terminar el chat.\n")
        session_id = self.create_session()
        if not session_id:
            print("Error al crear la sesión de chat.")
            return
        while True:
            query = input("\nTú: ")
            if query.lower() in ["salir", "exit", "quit"]:
                print("\n¡Hasta luego!")
                break
            print("\nBuscando información relevante...")
            response = self.generate_response(session_id, query)
            print(f"\nAsistente: {response}")

    def get_sessions(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de sesiones de chat.
        
        Returns:
            Lista de sesiones con id, created_at y updated_at
        """
        try:
            with psycopg2.connect(self.db_connection) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(
                        "SELECT id, created_at, updated_at FROM chat_sessions ORDER BY updated_at DESC"
                    )
                    return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            self.logger.error(f"Error al obtener sesiones: {e}")
            return []