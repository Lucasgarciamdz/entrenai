"""
Aplicación web Flask para el sistema RAG.
"""
import logging
import os
import sys
from flask import (
    Flask, render_template, request, jsonify, 
    session, redirect, url_for
)
from pathlib import Path
from core.utils import configurar_logging
from core.config import load_config
from rag.vector_store import VectorStore
from chat.manager import ChatManager

# Configurar logging
logger = configurar_logging("web_app")

def create_templates():
    """
    Crea plantillas básicas para la aplicación web.
    """
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    os.makedirs(templates_dir, exist_ok=True)

    # Plantilla base
    with open(os.path.join(templates_dir, 'base.html'), 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Asistente de Documentos Moodle{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" 
          rel="stylesheet">
    <style>
        .chat-container {
            max-height: 500px;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 10px;
        }
        .user-message {
            background-color: #e2f0ff;
            text-align: right;
            margin-left: 25%;
        }
        .assistant-message {
            background-color: #f0f0f0;
            margin-right: 25%;
        }
    </style>
    {% block head %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">Asistente Moodle</a>
            <button class="navbar-toggler" type="button" 
                    data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Chat</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/sessions">Sesiones</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/new_session">Nueva Sesión</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>""")

    # Plantilla de la página principal (chat)
    with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
        f.write("""{% extends 'base.html' %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <h1 class="mb-4">Chat con Asistente de Documentos Moodle</h1>

        <div id="chat-container" class="chat-container">
            <!-- Los mensajes del chat se cargarán aquí -->
        </div>

        <div class="input-group mb-3">
            <input type="text" id="user-input" class="form-control" 
                   placeholder="Escribe tu pregunta...">
            <button class="btn btn-primary" id="send-button">Enviar</button>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Cargar mensajes existentes
    loadMessages();

    // Enviar mensaje
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const query = userInput.value.trim();
        if (!query) return;

        // Añadir mensaje del usuario a la UI
        addMessageToUI('user', query);
        userInput.value = '';

        // Mostrar indicador de carga
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message assistant-message';
        loadingDiv.id = 'loading-message';
        loadingDiv.textContent = 'Buscando información...';
        chatContainer.appendChild(loadingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        // Enviar solicitud al servidor
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query }),
        })
        .then(response => response.json())
        .then(data => {
            // Eliminar indicador de carga
            const loadingMessage = document.getElementById('loading-message');
            if (loadingMessage) {
                loadingMessage.remove();
            }

            // Mostrar respuesta
            addMessageToUI('assistant', data.response);
        })
        .catch(error => {
            console.error('Error:', error);

            // Eliminar indicador de carga
            const loadingMessage = document.getElementById('loading-message');
            if (loadingMessage) {
                loadingMessage.remove();
            }

            // Mostrar mensaje de error
            addMessageToUI(
                'assistant', 
                'Lo siento, ocurrió un error al procesar tu solicitud.'
            );
        });
    }

    function addMessageToUI(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;

        // Formatear contenido con saltos de línea
        const formattedContent = content.replace(/\\n/g, '<br>');
        messageDiv.innerHTML = formattedContent;

        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function loadMessages() {
        fetch('/messages')
            .then(response => response.json())
            .then(data => {
                if (data.messages) {
                    chatContainer.innerHTML = '';
                    data.messages.forEach(message => {
                        addMessageToUI(message.role, message.content);
                    });
                }
            })
            .catch(error => {
                console.error('Error al cargar mensajes:', error);
            });
    }
});
</script>
{% endblock %}""")

    # Plantilla para listar sesiones
    with open(os.path.join(templates_dir, 'sessions.html'), 'w') as f:
        f.write("""{% extends 'base.html' %}

{% block title %}Sesiones de Chat - {{ super() }}{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <h1 class="mb-4">Sesiones de Chat</h1>

        <a href="/new_session" class="btn btn-primary mb-3">Nueva Sesión</a>

        <div class="list-group">
            {% if sessions %}
                {% for s in sessions %}
                <a href="/session/{{ s.id }}" 
                   class="list-group-item list-group-item-action">
                    <div class="d-flex w-100 justify-content-between">
                        <h5 class="mb-1">Sesión #{{ loop.index }}</h5>
                        <small>
                            Actualizado: 
                            {{ s.updated_at.strftime('%d/%m/%Y %H:%M') }}
                        </small>
                    </div>
                    <p class="mb-1">
                        Creado: {{ s.created_at.strftime('%d/%m/%Y %H:%M') }}
                    </p>
                </a>
                {% endfor %}
            {% else %}
                <div class="alert alert-info">No hay sesiones disponibles.</div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}""")

    # Plantilla para ver una sesión específica
    with open(os.path.join(templates_dir, 'session.html'), 'w') as f:
        f.write("""{% extends 'base.html' %}

{% block title %}Sesión de Chat - {{ super() }}{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <h1 class="mb-4">Sesión de Chat #{{ session_id[:8] }}</h1>

        <a href="/" class="btn btn-primary mb-3">Continuar esta conversación</a>
        <a href="/sessions" class="btn btn-secondary mb-3 ms-2">Volver a la lista</a>

        <div class="chat-container">
            {% if messages %}
                {% for message in messages %}
                <div class="message {{ message.role }}-message">
                    {{ message.content|replace('\\n', '<br>')|safe }}
                </div>
                {% endfor %}
            {% else %}
                <div class="alert alert-info">No hay mensajes en esta sesión.</div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}""")


def create_app(config_path=None):
    """
    Crea y configura la aplicación Flask.
    
    Args:
        config_path: Ruta al archivo de configuración
        
    Returns:
        Aplicación Flask configurada
    """
    app = Flask(__name__)
    app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'secreto-desarrollo')
    
    # Cargar configuración
    if config_path is None:
        config_path = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.yaml'))
    
    config = load_config(config_path)
    
    # Inicializar componentes
    # Configurar VectorStore con el proveedor de embeddings adecuado
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
        raise ValueError(f"Proveedor de embeddings no soportado: {embedding_provider}")
    
    chat_manager = ChatManager(
        qdrant_client=vector_store,
        db_connection=config['postgres']['connection_string'],
        ollama_url=config['ollama']['url'],
        model_name=config['ollama']['model_name']
    )
    
    # Crear plantillas si no existen
    create_templates()
    
    # Rutas
    @app.route('/')
    def index():
        """Página principal"""
        # Si no hay una sesión de chat activa, crear una
        if 'chat_session_id' not in session:
            chat_session_id = chat_manager.create_session()
            if chat_session_id:
                session['chat_session_id'] = chat_session_id
            else:
                return "Error al crear la sesión de chat", 500
    
        return render_template('index.html')
    
    @app.route('/chat', methods=['POST'])
    def chat():
        """Endpoint para el chat"""
        if 'chat_session_id' not in session:
            return jsonify({'error': 'No hay sesión de chat activa'}), 400
    
        # Obtener la consulta del usuario
        data = request.json
        if not data or 'query' not in data:
            return jsonify({'error': 'Se requiere una consulta'}), 400
    
        query = data['query']
    
        # Generar respuesta
        response = chat_manager.generate_response(
            session['chat_session_id'], 
            query
        )
    
        return jsonify({
            'response': response
        })
    
    @app.route('/sessions')
    def list_sessions():
        """Listar sesiones de chat"""
        sessions = chat_manager.get_sessions()
        return render_template('sessions.html', sessions=sessions)
    
    @app.route('/session/<session_id>')
    def view_session(session_id):
        """Ver una sesión específica"""
        # Establecer la sesión activa
        session['chat_session_id'] = session_id
    
        # Obtener mensajes
        messages = chat_manager.get_session_messages(session_id)
    
        return render_template(
            'session.html', 
            messages=messages, 
            session_id=session_id
        )
    
    @app.route('/new_session')
    def new_session():
        """Crear una nueva sesión"""
        chat_session_id = chat_manager.create_session()
        if chat_session_id:
            session['chat_session_id'] = chat_session_id
            return redirect(url_for('index'))
        else:
            return "Error al crear la sesión de chat", 500
    
    @app.route('/messages')
    def get_messages():
        """Obtener mensajes de la sesión actual (para AJAX)"""
        if 'chat_session_id' not in session:
            return jsonify({'error': 'No hay sesión de chat activa'}), 400
    
        messages = chat_manager.get_session_messages(session['chat_session_id'])
        return jsonify({'messages': messages})
    
    return app


def run_app(host='0.0.0.0', port=5000, debug=True):
    """
    Ejecuta la aplicación web.
    
    Args:
        host: Host donde escuchar
        port: Puerto donde escuchar
        debug: Modo debug
    """
    app = create_app()
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_app()