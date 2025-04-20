"""
Gestor para el fine-tuning de modelos LLM.
"""
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import psycopg2
from psycopg2.extras import DictCursor
from core.utils import configurar_logging
from core.config import load_config

# Para OpenAI (opcional)
try:
    import openai
except ImportError:
    openai = None


class FineTuningManager:
    """
    Gestor para el fine-tuning de modelos LLM
    """
    
    def __init__(
        self,
        db_connection: str,
        provider: str = "openai",
        openai_api_key: Optional[str] = None,
        openai_model: str = "gpt-3.5-turbo",
        output_dir: str = "fine_tuning_data"
    ):
        """
        Inicializa el gestor de fine-tuning
        
        Args:
            db_connection: Cadena de conexión a PostgreSQL para obtener datos de chat
            provider: Proveedor para fine-tuning ("openai" o "local")
            openai_api_key: Clave API de OpenAI (requerida si provider="openai")
            openai_model: Modelo base de OpenAI para fine-tuning
            output_dir: Directorio para guardar archivos de fine-tuning
        """
        self.db_connection = db_connection
        self.provider = provider
        self.output_dir = output_dir
        self.logger = configurar_logging('fine_tuning')
        
        # Crear directorio de salida si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Configuración específica del proveedor
        if provider == "openai":
            if not openai_api_key and not os.environ.get("OPENAI_API_KEY"):
                raise ValueError("Se requiere openai_api_key o la variable de entorno OPENAI_API_KEY cuando provider='openai'")
            if openai is None:
                raise ImportError("El paquete 'openai' no está instalado. Instálalo con 'pip install openai'")
            
            # Configurar cliente de OpenAI
            self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
            self.openai_model = openai_model
            openai.api_key = self.openai_api_key
        elif provider == "local":
            # Para fine-tuning local, no se requiere configuración adicional
            pass
        else:
            raise ValueError("provider debe ser 'openai' o 'local'")
    
    def get_chat_data(self) -> List[Dict[str, Any]]:
        """
        Obtiene datos de chat de la base de datos para fine-tuning
        
        Returns:
            Lista de conversaciones con mensajes
        """
        try:
            with psycopg2.connect(self.db_connection) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    # Obtener todas las sesiones
                    cur.execute("""
                        SELECT id, created_at, updated_at 
                        FROM chat_sessions 
                        ORDER BY updated_at DESC
                    """)
                    
                    sessions = []
                    for session_row in cur.fetchall():
                        session_id = session_row['id']
                        
                        # Obtener mensajes de la sesión
                        cur.execute("""
                            SELECT sender as role, content, timestamp as created_at
                            FROM chat_messages
                            WHERE session_id = %s
                            ORDER BY timestamp ASC
                        """, (session_id,))
                        
                        messages = []
                        for msg_row in cur.fetchall():
                            messages.append({
                                'role': msg_row['role'],
                                'content': msg_row['content'],
                                'created_at': msg_row['created_at'].isoformat(),
                                'metadata': {}
                            })
                        
                        # Solo incluir sesiones con al menos una pregunta y respuesta
                        if len(messages) >= 2:
                            sessions.append({
                                'id': session_id,
                                'created_at': session_row['created_at'].isoformat(),
                                'updated_at': session_row['updated_at'].isoformat(),
                                'messages': messages
                            })
                    
                    self.logger.info(f"Se obtuvieron {len(sessions)} sesiones de chat para fine-tuning")
                    return sessions
        
        except Exception as e:
            self.logger.error(f"Error al obtener datos de chat: {e}")
            return []
    
    def prepare_openai_data(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepara los datos en el formato requerido por OpenAI para fine-tuning
        
        Args:
            sessions: Lista de sesiones de chat
        
        Returns:
            Lista de ejemplos en formato OpenAI
        """
        examples = []
        
        for session in sessions:
            messages = session['messages']
            
            # Filtrar mensajes válidos (solo user y assistant)
            valid_messages = [
                msg for msg in messages 
                if msg['role'] in ['user', 'assistant'] and msg['content'].strip()
            ]
            
            # Agrupar mensajes en pares de pregunta-respuesta
            for i in range(0, len(valid_messages) - 1, 2):
                if i + 1 < len(valid_messages):
                    user_msg = valid_messages[i]
                    assistant_msg = valid_messages[i + 1]
                    
                    # Verificar que sea un par user-assistant
                    if user_msg['role'] == 'user' and assistant_msg['role'] == 'assistant':
                        example = {
                            "messages": [
                                {"role": "system", "content": "Eres un asistente útil que responde preguntas basadas en la información proporcionada."},
                                {"role": "user", "content": user_msg['content']},
                                {"role": "assistant", "content": assistant_msg['content']}
                            ]
                        }
                        examples.append(example)
        
        self.logger.info(f"Se prepararon {len(examples)} ejemplos para fine-tuning con OpenAI")
        return examples
    
    def prepare_local_data(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepara los datos en un formato simple para fine-tuning local
        
        Args:
            sessions: Lista de sesiones de chat
        
        Returns:
            Lista de ejemplos en formato simple
        """
        examples = []
        
        for session in sessions:
            messages = session['messages']
            
            # Filtrar mensajes válidos (solo user y assistant)
            valid_messages = [
                msg for msg in messages 
                if msg['role'] in ['user', 'assistant'] and msg['content'].strip()
            ]
            
            # Agrupar mensajes en pares de pregunta-respuesta
            for i in range(0, len(valid_messages) - 1, 2):
                if i + 1 < len(valid_messages):
                    user_msg = valid_messages[i]
                    assistant_msg = valid_messages[i + 1]
                    
                    # Verificar que sea un par user-assistant
                    if user_msg['role'] == 'user' and assistant_msg['role'] == 'assistant':
                        example = {
                            "instruction": user_msg['content'],
                            "response": assistant_msg['content']
                        }
                        examples.append(example)
        
        self.logger.info(f"Se prepararon {len(examples)} ejemplos para fine-tuning local")
        return examples
    
    def save_training_data(self, data: List[Dict[str, Any]], filename: str):
        """
        Guarda los datos de entrenamiento en un archivo
        
        Args:
            data: Datos de entrenamiento
            filename: Nombre del archivo
            
        Returns:
            Ruta al archivo guardado o None en caso de error
        """
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                if filename.endswith('.jsonl'):
                    # Formato JSONL (una línea por ejemplo)
                    for example in data:
                        f.write(json.dumps(example, ensure_ascii=False) + '\n')
                else:
                    # Formato JSON normal
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Datos de entrenamiento guardados en {filepath}")
            return filepath
        
        except Exception as e:
            self.logger.error(f"Error al guardar datos de entrenamiento: {e}")
            return None
    
    def start_openai_fine_tuning(self, data_file: str) -> Optional[str]:
        """
        Inicia un trabajo de fine-tuning con OpenAI
        
        Args:
            data_file: Ruta al archivo de datos de entrenamiento
        
        Returns:
            ID del trabajo de fine-tuning o None en caso de error
        """
        if openai is None:
            self.logger.error("No se puede iniciar fine-tuning con OpenAI: el paquete 'openai' no está instalado")
            return None
        
        try:
            # Crear archivo en OpenAI
            with open(data_file, 'rb') as f:
                response = openai.files.create(
                    file=f,
                    purpose="fine-tune"
                )
            file_id = response.id
            
            # Iniciar trabajo de fine-tuning
            response = openai.fine_tuning.jobs.create(
                training_file=file_id,
                model=self.openai_model
            )
            
            job_id = response.id
            self.logger.info(f"Trabajo de fine-tuning iniciado con ID: {job_id}")
            
            return job_id
            
        except Exception as e:
            self.logger.error(f"Error al iniciar fine-tuning con OpenAI: {e}")
            return None
    
    def run_fine_tuning(self):
        """
        Ejecuta el proceso completo de fine-tuning
        
        Returns:
            True si el proceso se completó correctamente, False en caso contrario
        """
        # Obtener datos de chat
        sessions = self.get_chat_data()
        if not sessions:
            self.logger.error("No hay datos suficientes para fine-tuning")
            return False
        
        # Preparar datos según el proveedor
        if self.provider == "openai":
            data = self.prepare_openai_data(sessions)
            data_file = self.save_training_data(data, "openai_training_data.jsonl")
            
            if data_file:
                job_id = self.start_openai_fine_tuning(data_file)
                return job_id is not None
            return False
            
        elif self.provider == "local":
            data = self.prepare_local_data(sessions)
            data_file = self.save_training_data(data, "local_training_data.json")
            
            if data_file:
                self.logger.info(f"""
                Para realizar fine-tuning local, utiliza el archivo {data_file} con tu herramienta preferida.
                
                Ejemplo con Ollama:
                1. Crea un Modelfile con el contenido:
                   FROM llama3
                   TEMPLATE "<|im_start|>
                   {{#system~}}
                   Eres un asistente útil que responde preguntas basadas en la información proporcionada.
                   {{~/system}}
                   
                   {{#user~}}
                   {{instruction}}
                   {{~/user}}
                   
                   {{#assistant~}}
                   {{response}}
                   {{~/assistant}}
                   <|im_end|>"
                   
                2. Ejecuta: ollama create moodle-assistant -f Modelfile
                3. Ejecuta: ollama tune moodle-assistant {data_file}
                """)
                return True
            return False
        
        return False


def run_fine_tuning(config_path=None, provider="local"):
    """
    Ejecuta el proceso de fine-tuning con la configuración especificada.
    
    Args:
        config_path: Ruta al archivo de configuración
        provider: Proveedor para fine-tuning ("openai" o "local")
        
    Returns:
        True si el proceso se completó correctamente, False en caso contrario
    """
    # Configurar logging
    logger = configurar_logging("fine_tuning_main")
    
    # Cargar configuración
    if config_path is None:
        config_path = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.yaml'))
    
    config = load_config(config_path)
    
    # Inicializar gestor de fine-tuning
    if provider == 'openai':
        fine_tuning_manager = FineTuningManager(
            db_connection=config['postgres']['connection_string'],
            provider='openai',
            openai_api_key=config['embeddings']['openai_api_key'],
            openai_model='gpt-3.5-turbo'
        )
    else:
        fine_tuning_manager = FineTuningManager(
            db_connection=config['postgres']['connection_string'],
            provider='local'
        )
    
    # Ejecutar fine-tuning
    result = fine_tuning_manager.run_fine_tuning()
    
    if result:
        logger.info("Proceso de fine-tuning completado correctamente")
    else:
        logger.error("Error en el proceso de fine-tuning")
    
    return result