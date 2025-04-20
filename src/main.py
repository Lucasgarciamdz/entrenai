#!/usr/bin/env python3
"""
Punto de entrada principal para el sistema RAG de Moodle.

Este script proporciona una interfaz unificada para todas las funcionalidades
del sistema: indexación de documentos, chat interactivo, interfaz web y fine-tuning.
"""
import argparse
from pathlib import Path

from chat.manager import ChatManager
from core.config import load_config
from core.utils import configurar_logging
from fine_tuning.manager import run_fine_tuning
from moodle.client import MoodleClient
from rag.document_processor import DocumentProcessor
from rag.vector_store import VectorStore
from web.app import run_app
import os

# Configurar logging
logger = configurar_logging("main")
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def indexar_documentos(config):
  """
  Descarga e indexa documentos de Moodle.

  Args:
      config: Configuración del sistema
  """
  logger.info("Iniciando indexación de documentos de Moodle")

  # Inicializar cliente de Moodle
  moodle_client = MoodleClient(
      url=config['moodle']['url'],
      token=config['moodle']['token']
  )

  # Inicializar procesador de documentos
  doc_processor = DocumentProcessor()

  # Inicializar VectorStore
  embedding_provider = config['embeddings']['provider']
  if embedding_provider == 'ollama':
    vector_store = VectorStore(
        host=config['qdrant']['host'],
        port=config['qdrant']['port'],
        collection_name=config['qdrant']['collection_name'],
        embedding_provider='ollama',
        ollama_url=config['ollama']['url']
    )
  elif embedding_provider == 'openai':
    vector_store = VectorStore(
        host=config['qdrant']['host'],
        port=config['qdrant']['port'],
        collection_name=config['qdrant']['collection_name'],
        embedding_provider='openai',
        openai_api_key=config['embeddings']['openai_api_key'],
        openai_model=config['embeddings']['openai_model']
    )
  else:
    logger.error(f"Proveedor de embeddings no soportado: {embedding_provider}")
    return

  # Obtener cursos
  try:
    cursos = moodle_client.get_courses()
    if not cursos:
      logger.error("No se encontraron cursos en Moodle")
      return

    # Buscar el curso objetivo
    curso_objetivo = None
    for curso in cursos:
      if curso.get('shortname') == config['moodle']['target_course']:
        curso_objetivo = curso
        break

    if not curso_objetivo:
      logger.error(
        f"No se encontró el curso '{config['moodle']['target_course']}'")
      logger.info("Cursos disponibles:")
      for curso in cursos:
        logger.info(f"  - {curso.get('shortname')}: {curso.get('fullname')}")
      return

    logger.info(f"Procesando curso: {curso_objetivo.get('fullname')}")

    # Obtener contenido del curso
    contenido = moodle_client.get_course_contents(curso_objetivo.get('id'))

    # Procesar cada sección y módulo
    for seccion in contenido:
      logger.info(f"Procesando sección: {seccion.get('name')}")

      for modulo in seccion.get('modules', []):
        nombre_modulo = modulo.get('name')
        tipo_modulo = modulo.get('modname')

        # Procesar archivos
        if 'contents' in modulo:
          for contenido in modulo.get('contents', []):
            if 'fileurl' in contenido:
              nombre_archivo = contenido.get('filename')
              url_archivo = contenido.get('fileurl')

              logger.info(f"Descargando archivo: {nombre_archivo}")
              try:
                # Descargar archivo
                contenido_archivo, tipo_contenido = moodle_client.download_file(
                    url_archivo, nombre_archivo
                )

                # Procesar documento
                texto, metadata = doc_processor.process_document(
                    contenido_archivo, tipo_contenido, nombre_archivo
                )

                if texto:
                  # Añadir metadatos adicionales
                  metadata.update({
                    'course': curso_objetivo.get('fullname'),
                    'section': seccion.get('name'),
                    'module': nombre_modulo,
                    'module_type': tipo_modulo
                  })

                  # Indexar documento
                  logger.info(f"Indexando documento: {nombre_archivo}")
                  vector_store.index_document(texto, metadata)
                else:
                  logger.warning(
                    f"No se pudo extraer texto de {nombre_archivo}")

              except Exception as e:
                logger.error(f"Error al procesar {nombre_archivo}: {e}")

    logger.info("Indexación de documentos completada")

  except Exception as e:
    logger.error(f"Error durante la indexación: {e}")


def iniciar_chat(config):
  """
  Inicia el chat interactivo en la consola.

  Args:
      config: Configuración del sistema
  """
  logger.info("Iniciando chat interactivo")

  # Inicializar VectorStore (embeddings: ollama/openai only)
  embedding_provider = config['embeddings']['provider']
  if embedding_provider == 'ollama':
    vector_store = VectorStore(
        host=config['qdrant']['host'],
        port=config['qdrant']['port'],
        collection_name=config['qdrant']['collection_name'],
        embedding_provider='ollama',
        ollama_url=config['ollama']['url']
    )
  elif embedding_provider == 'openai':
    vector_store = VectorStore(
        host=config['qdrant']['host'],
        port=config['qdrant']['port'],
        collection_name=config['qdrant']['collection_name'],
        embedding_provider='openai',
        openai_api_key=config['embeddings']['openai_api_key'],
        openai_model=config['embeddings']['openai_model']
    )
  else:
    logger.error(f"Proveedor de embeddings no soportado: {embedding_provider}")
    return

  # Selección de modelo de chat
  chat_model = config['ollama']['model_name']
  chat_url = config['ollama']['url']
  if 'bitnet' in config and config['bitnet'].get('model_name'):
    # Permitir override por env/config: si BITNET_MODEL está seteado, usarlo
    chat_model = config['bitnet']['model_name']
    chat_url = ""  # BitNet no requiere URL

  # Inicializar ChatManager
  chat_manager = ChatManager(
      qdrant_client=vector_store,
      db_connection=config['postgres']['connection_string'],
      ollama_url=chat_url,
      model_name=chat_model
  )

  # Iniciar chat interactivo
  chat_manager.start_interactive_chat()


def iniciar_web(host='0.0.0.0', port=5000, debug=True):
  """
  Inicia la aplicación web.

  Args:
      host: Host donde escuchar
      port: Puerto donde escuchar
      debug: Modo debug
  """
  logger.info(f"Iniciando aplicación web en {host}:{port}")
  run_app(host=host, port=port, debug=debug)


def main():
  """Función principal que procesa los argumentos de línea de comandos."""
  parser = argparse.ArgumentParser(description="Sistema RAG para Moodle")

  # Argumentos mutuamente excluyentes
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument('--index', action='store_true',
                     help='Indexar documentos de Moodle')
  group.add_argument('--chat', action='store_true',
                     help='Iniciar chat interactivo')
  group.add_argument('--web', action='store_true',
                     help='Iniciar aplicación web')
  group.add_argument('--fine-tune', action='store_true',
                     help='Realizar fine-tuning del modelo')

  # Argumentos opcionales
  parser.add_argument('--config', type=str,
                      help='Ruta al archivo de configuración')
  parser.add_argument('--provider', type=str, choices=['local', 'openai'],
                      default='local', help='Proveedor para fine-tuning')

  args = parser.parse_args()

  # Cargar configuración
  config_path = Path(args.config) if args.config else Path('./config.yaml')
  config = load_config(config_path)

  # Ejecutar la acción correspondiente
  if args.index:
    indexar_documentos(config)
  elif args.chat:
    iniciar_chat(config)
  elif args.web:
    iniciar_web()
  elif args.fine_tune:
    run_fine_tuning(config_path, args.provider)


if __name__ == "__main__":
  main()
