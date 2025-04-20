"""
Gestión de configuración para el sistema RAG.

Este módulo maneja la carga de configuración desde archivos YAML y variables de entorno.
"""
import os
import yaml
from pathlib import Path


def load_config(config_path):
    """
    Carga la configuración desde un archivo YAML y aplica variables de entorno.
    
    Args:
        config_path: Ruta al archivo de configuración YAML
        
    Returns:
        Diccionario con la configuración cargada
    """
    if not config_path.exists():
        # Si no existe el archivo de configuración, creamos una configuración por defecto
        config = {
            'moodle': {
                'url': os.environ.get('MOODLE_URL', 'http://moodle:8080'),
                'token': os.environ.get('MOODLE_TOKEN', ''),
                'target_course': os.environ.get('MOODLE_TARGET_COURSE', 'prueba')
            },
            'qdrant': {
                'host': os.environ.get('QDRANT_HOST', 'localhost'),
                'port': int(os.environ.get('QDRANT_PORT', 6333)),
                'collection_name': os.environ.get('QDRANT_COLLECTION', 'moodle_docs')
            },
            'embeddings': {
                'provider': os.environ.get('EMBEDDING_PROVIDER', 'ollama'),
                'openai_api_key': os.environ.get('OPENAI_API_KEY', ''),
                'openai_model': os.environ.get('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
            },
            'ollama': {
                'url': os.environ.get('OLLAMA_URL', 'http://localhost:11434'),
                'model_name': os.environ.get('OLLAMA_MODEL', 'llama3:8b')
            },
            'postgres': {
                'connection_string': os.environ.get(
                    'POSTGRES_CONNECTION', 
                    'postgresql://n8n:n8n_password@localhost:5432/n8n'
                )
            }
        }
    else:
        # Cargar desde archivo YAML
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Aplicar variables de entorno sobre la configuración cargada
        if 'MOODLE_URL' in os.environ:
            config['moodle']['url'] = os.environ['MOODLE_URL']
        if 'MOODLE_TOKEN' in os.environ:
            config['moodle']['token'] = os.environ['MOODLE_TOKEN']
        if 'MOODLE_TARGET_COURSE' in os.environ:
            config['moodle']['target_course'] = os.environ['MOODLE_TARGET_COURSE']

        if 'QDRANT_HOST' in os.environ:
            config['qdrant']['host'] = os.environ['QDRANT_HOST']
        if 'QDRANT_PORT' in os.environ:
            config['qdrant']['port'] = int(os.environ['QDRANT_PORT'])
        if 'QDRANT_COLLECTION' in os.environ:
            config['qdrant']['collection_name'] = os.environ['QDRANT_COLLECTION']

        if 'EMBEDDING_PROVIDER' in os.environ:
            config['embeddings']['provider'] = os.environ['EMBEDDING_PROVIDER']
        if 'OPENAI_API_KEY' in os.environ:
            config['embeddings']['openai_api_key'] = os.environ['OPENAI_API_KEY']
        if 'OPENAI_EMBEDDING_MODEL' in os.environ:
            config['embeddings']['openai_model'] = os.environ['OPENAI_EMBEDDING_MODEL']

        if 'OLLAMA_URL' in os.environ:
            config['ollama']['url'] = os.environ['OLLAMA_URL']
        if 'OLLAMA_MODEL' in os.environ:
            config['ollama']['model_name'] = os.environ['OLLAMA_MODEL']

        if 'POSTGRES_CONNECTION' in os.environ:
            config['postgres']['connection_string'] = os.environ['POSTGRES_CONNECTION']

    return config


def save_default_config(config_path=None):
    """
    Guarda una configuración por defecto en el archivo especificado.
    
    Args:
        config_path: Ruta donde guardar el archivo de configuración
        
    Returns:
        Ruta al archivo de configuración guardado
    """
    if config_path is None:
        config_path = Path('config.yaml')

    config = load_config(Path('nonexistent_file.yaml'))

    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

    return config_path