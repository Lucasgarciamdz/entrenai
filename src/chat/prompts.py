"""
Plantillas de prompts reutilizables para el sistema RAG. Todas en español.
"""

PROMPT_BUSQUEDA="""
Eres un asistente académico. Responde de forma clara y concisa usando solo la información relevante encontrada en los documentos del curso.
Pregunta del usuario: {pregunta}
Fragmentos relevantes:
{contexto}
Respuesta:
"""

PROMPT_CHAT="""
Actúa como tutor virtual. Usa la información de los documentos y responde en español, siendo breve y directo.
Conversación previa:
{historial}
Pregunta:
{pregunta}
Respuesta:
"""

PROMPT_RERANKING="""
Dado los siguientes fragmentos, ordena del más relevante al menos relevante para la pregunta: {pregunta}
Fragmentos:
{fragmentos}
Lista ordenada:
"""