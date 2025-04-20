"""
Utilidades generales y configuración de logging para el sistema RAG.
"""
import logging

def configurar_logging(nombre="sistema-rag", nivel=logging.INFO, archivo="moodle_rag.log"):
    """
    Configura y devuelve un logger con el nombre especificado.
    
    Args:
        nombre: Nombre del logger
        nivel: Nivel de logging (por defecto INFO)
        archivo: Nombre del archivo de log
        
    Returns:
        Un objeto logger configurado
    """
    logging.basicConfig(
        level=nivel,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(archivo)
        ]
    )
    return logging.getLogger(nombre)