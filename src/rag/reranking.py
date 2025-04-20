"""
Implementación simple de reranking para fragmentos recuperados.
"""
from typing import List

def rerank_fragments(pregunta: str, fragmentos: List[str]) -> List[str]:
    """
    Ordena los fragmentos según la presencia de palabras clave de la pregunta.
    
    Args:
        pregunta: Pregunta del usuario
        fragmentos: Lista de fragmentos de texto a ordenar
        
    Returns:
        Lista de fragmentos ordenados por relevancia
    """
    palabras = set(pregunta.lower().split())
    
    def score(frag):
        """Calcula la puntuación de un fragmento basado en las palabras clave."""
        return sum(1 for p in palabras if p in frag.lower())
    
    return sorted(fragmentos, key=score, reverse=True)