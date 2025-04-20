"""
Gestión de configuración para el sistema RAG.

Este módulo maneja la carga de configuración desde archivos YAML y variables de entorno.
"""
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
import re

def _interpolate_env_vars(obj):
    """
    Recursively interpolate ${VAR} in strings using environment variables.
    """
    if isinstance(obj, dict):
        return {k: _interpolate_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_interpolate_env_vars(i) for i in obj]
    elif isinstance(obj, str):
        # Replace ${VAR} with environment variable value
        def replacer(match):
            var = match.group(1)
            return os.environ.get(var, match.group(0))
        return re.sub(r'\${([A-Za-z0-9_]+)}', replacer, obj)
    else:
        return obj

def load_config(config_path):
    """
    Carga la configuración desde un archivo YAML interpolando variables de entorno.
    Args:
        config_path: Ruta al archivo de configuración YAML
    Returns:
        Diccionario con la configuración cargada
    """
    # Cargar .env primero
    dotenv_path = Path(config_path).parent / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path, override=True)
    # Cargar YAML
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    # Interpolar variables de entorno
    config = _interpolate_env_vars(config)
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
    config = {
        'moodle': {
            'url': '${MOODLE_URL}',
            'token': '${MOODLE_TOKEN}',
            'target_course': '${MOODLE_TARGET_COURSE}'
        },
        'qdrant': {
            'host': '${QDRANT_HOST}',
            'port': '${QDRANT_PORT}',
            'collection_name': '${QDRANT_COLLECTION}'
        },
        'embeddings': {
            'provider': '${EMBEDDING_PROVIDER}',
            'openai_api_key': '${OPENAI_API_KEY}',
            'openai_model': '${OPENAI_EMBEDDING_MODEL}'
        },
        'ollama': {
            'url': '${OLLAMA_URL}',
            'model_name': '${OLLAMA_MODEL}'
        },
        'bitnet': {
            'model_name': '${BITNET_MODEL}'
        },
        'postgres': {
            'connection_string': '${POSTGRES_CONNECTION}'
        }
    }
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False)
    return config_path