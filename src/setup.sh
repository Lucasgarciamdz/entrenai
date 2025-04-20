#!/bin/bash
# Script para configurar el entorno de desarrollo

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado"
    echo "Por favor, instala Python 3 antes de continuar"
    exit 1
fi

# Crear entorno virtual
echo "Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate

# Verificar que pip está disponible
if ! command -v pip &> /dev/null; then
    echo "Error: pip no está disponible en el entorno virtual"
    echo "Intenta reinstalar el entorno virtual"
    exit 1
fi

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# Verificar si las dependencias clave se instalaron correctamente
echo "Verificando dependencias clave..."

if python -c "import flask" &> /dev/null; then
    echo "✓ Flask instalado correctamente"
else
    echo "✗ Error al instalar Flask"
fi

if python -c "import qdrant_client" &> /dev/null; then
    echo "✓ Qdrant Client instalado correctamente"
else
    echo "✗ Error al instalar Qdrant Client"
fi

if python -c "import psycopg2" &> /dev/null; then
    echo "✓ Psycopg2 instalado correctamente"
else
    echo "✗ Error al instalar Psycopg2"
fi

# Verificar si existe config.yaml
if [ ! -f config.yaml ]; then
    echo "Creando archivo de configuración por defecto..."
    python -c "from config import save_default_config; save_default_config()"
fi

# Instrucciones finales
echo ""
echo "=================================="
echo "Configuración completada"
echo "=================================="
echo ""
echo "Para activar el entorno virtual:"
echo "  source venv/bin/activate"
echo ""
echo "Para indexar documentos de Moodle:"
echo "  python main.py --index"
echo ""
echo "Para iniciar el chat interactivo:"
echo "  python main.py --chat"
echo ""
echo "Para iniciar la aplicación web:"
echo "  python main.py --web"
echo ""
echo "No olvides configurar tu token de Moodle en config.yaml o como variable de entorno:"
echo "  export MOODLE_TOKEN=tu_token_de_moodle"
echo ""
echo "Asegúrate de tener los servicios de Docker Compose en ejecución:"
echo "  docker-compose up -d"
echo "" 
