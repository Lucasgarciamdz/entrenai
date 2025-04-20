"""
Definición de errores personalizados para el sistema RAG.
"""

class ErrorRAG(Exception):
    """Error base para el sistema RAG."""

class ErrorMoodle(ErrorRAG):
    """Error al interactuar con Moodle."""

class ErrorProcesamientoDocumento(ErrorRAG):
    """Error en el procesamiento de documentos."""

class ErrorVectorDB(ErrorRAG):
    """Error en la base de datos vectorial."""

class ErrorChat(ErrorRAG):
    """Error en el gestor de chat."""