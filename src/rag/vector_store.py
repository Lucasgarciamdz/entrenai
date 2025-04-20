"""
Wrapper para interactuar con Qdrant y generar embeddings con Ollama o OpenAI.
"""
import os
import requests
from typing import Dict, List, Any, Literal, cast
from uuid import uuid4
from core.utils import configurar_logging
from core.errors import ErrorVectorDB
from qdrant_client import QdrantClient
from qdrant_client.http import models

try:
    import openai
except ImportError:
    openai = None

class VectorStore:
    """
    Wrapper para interactuar con Qdrant y generar embeddings con Ollama o OpenAI
    """
    def __init__(
        self, 
        host: str, 
        port: int, 
        collection_name: str, 
        ollama_url: str = "",
        embedding_provider: Literal["ollama", "openai"] = "ollama",
        openai_api_key: str = "",
        openai_model: str = "text-embedding-3-small"
    ):
        """
        Inicializa el almacén de vectores.
        
        Args:
            host: Host de Qdrant
            port: Puerto de Qdrant
            collection_name: Nombre de la colección en Qdrant
            ollama_url: URL de Ollama (requerido si embedding_provider='ollama')
            embedding_provider: Proveedor de embeddings ('ollama' o 'openai')
            openai_api_key: Clave API de OpenAI (requerida si embedding_provider='openai')
            openai_model: Modelo de embeddings de OpenAI
            
        Raises:
            ValueError: Si faltan parámetros requeridos según el proveedor
        """
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.embedding_provider = embedding_provider
        self.logger = configurar_logging("vector_store")
        
        if embedding_provider == "ollama":
            if not ollama_url:
                raise ValueError("Se requiere ollama_url cuando embedding_provider='ollama'")
            self.ollama_url = ollama_url
            self.ollama_model = "nomic-embed-text"
        elif embedding_provider == "openai":
            if not openai_api_key and not os.environ.get("OPENAI_API_KEY"):
                raise ValueError("Se requiere openai_api_key cuando embedding_provider='openai'")
            self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
            self.openai_model = openai_model
            if openai:
                openai.api_key = self.openai_api_key
        else:
            raise ValueError("embedding_provider debe ser 'ollama' o 'openai'")

    def _generate_embedding(self, texto: str) -> List[float]:
        """
        Genera un embedding para el texto dado.
        
        Args:
            texto: Texto para generar el embedding
            
        Returns:
            Lista de valores float que representan el embedding
            
        Raises:
            ErrorVectorDB: Si ocurre un error al generar el embedding
        """
        try:
            if self.embedding_provider == "ollama":
                response = requests.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={"model": self.ollama_model, "prompt": texto},
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                return data["embedding"]
            elif self.embedding_provider == "openai" and openai:
                response = openai.embeddings.create(
                    input=texto,
                    model=self.openai_model
                )
                return response.data[0].embedding
            else:
                self.logger.error("Proveedor de embeddings no soportado o no inicializado")
                raise ErrorVectorDB("Proveedor de embeddings no soportado")
        except Exception as e:
            self.logger.error(f"Error al generar embedding: {e}")
            raise ErrorVectorDB(str(e))

    def index_document(self, texto: str, metadata: Dict[str, Any]) -> bool:
        """
        Indexa un documento en Qdrant.
        
        Args:
            texto: Texto del documento
            metadata: Metadatos del documento
            
        Returns:
            True si se indexó correctamente
            
        Raises:
            ErrorVectorDB: Si ocurre un error al indexar el documento
        """
        try:
            # Dividir el texto en chunks para evitar límites de tamaño
            chunks = [texto[i:i+512] for i in range(0, len(texto), 512)]
            for i, chunk in enumerate(chunks):
                embedding = self._generate_embedding(chunk)
                point_id = str(uuid4())
                chunk_metadata = dict(metadata)
                chunk_metadata.update({
                    "chunk": i,
                    "total_chunks": len(chunks),
                    "chunk_text": chunk[:200] + "..." if len(chunk) > 200 else chunk
                })
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=[
                        models.PointStruct(
                            id=point_id,
                            vector=embedding,
                            payload=chunk_metadata
                        )
                    ]
                )
            return True
        except Exception as e:
            self.logger.error(f"Error al indexar documento en Qdrant: {e}")
            raise ErrorVectorDB(str(e))

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Busca documentos similares a la consulta.
        
        Args:
            query: Consulta de búsqueda
            limit: Número máximo de resultados
            
        Returns:
            Lista de documentos similares con sus metadatos y puntuación
            
        Raises:
            ErrorVectorDB: Si ocurre un error al buscar
        """
        query_embedding = self._generate_embedding(query)
        if not query_embedding:
            self.logger.error("No se pudo generar el embedding para la consulta")
            return []
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit
            )
            results = []
            for point in search_result:
                if point.payload:
                    results.append({
                        'score': point.score,
                        **cast(Dict[str, Any], point.payload),
                    })
            return results
        except Exception as e:
            self.logger.error(f"Error al buscar en Qdrant: {e}")
            raise ErrorVectorDB(str(e))