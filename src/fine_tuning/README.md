# Módulo Fine-Tuning

Este módulo proporciona herramientas para realizar fine-tuning de modelos de lenguaje utilizando datos de conversaciones del sistema RAG.

## Propósito

El módulo `fine_tuning` permite:

1. Extraer datos de conversaciones almacenadas en la base de datos
2. Preparar estos datos en el formato adecuado para fine-tuning
3. Realizar fine-tuning de modelos de lenguaje, ya sea:
   - Localmente con Ollama
   - En la nube con OpenAI

El objetivo es mejorar la calidad de las respuestas del sistema adaptando los modelos a las conversaciones específicas del dominio educativo.

## Componentes

### manager.py

Este archivo contiene la clase `FineTuningManager` que se encarga de:

- Obtener datos de chat de la base de datos PostgreSQL
- Preparar los datos en el formato adecuado según el proveedor (OpenAI o local)
- Guardar los datos de entrenamiento en archivos JSON o JSONL
- Iniciar trabajos de fine-tuning con OpenAI
- Proporcionar instrucciones para fine-tuning local con Ollama

También incluye la función `run_fine_tuning` que simplifica el proceso de fine-tuning desde la línea de comandos.

## Uso

### Fine-tuning con OpenAI

```python
from fine_tuning.manager import FineTuningManager

# Inicializar el gestor de fine-tuning para OpenAI
fine_tuning_manager = FineTuningManager(
    db_connection="postgresql://usuario:contraseña@localhost:5432/basededatos",
    provider="openai",
    openai_api_key="tu_api_key_de_openai",
    openai_model="gpt-3.5-turbo"
)

# Ejecutar el proceso completo de fine-tuning
resultado = fine_tuning_manager.run_fine_tuning()

if resultado:
    print("Fine-tuning iniciado correctamente")
else:
    print("Error al iniciar fine-tuning")
```

### Fine-tuning local con Ollama

```python
from fine_tuning.manager import FineTuningManager

# Inicializar el gestor de fine-tuning para uso local
fine_tuning_manager = FineTuningManager(
    db_connection="postgresql://usuario:contraseña@localhost:5432/basededatos",
    provider="local",
    output_dir="datos_fine_tuning"
)

# Ejecutar el proceso de preparación de datos
resultado = fine_tuning_manager.run_fine_tuning()

# El resultado incluirá instrucciones para realizar el fine-tuning con Ollama
```

### Desde línea de comandos

```bash
# Fine-tuning local (con Ollama)
python main.py --fine-tune --provider local

# Fine-tuning con OpenAI
python main.py --fine-tune --provider openai
```

## Formatos de datos

### Formato para OpenAI

```json
{
  "messages": [
    {"role": "system", "content": "Eres un asistente útil que responde preguntas basadas en la información proporcionada."},
    {"role": "user", "content": "¿Cuál es la fórmula de la energía?"},
    {"role": "assistant", "content": "La fórmula de la energía es E=mc², donde E es energía, m es masa y c es la velocidad de la luz."}
  ]
}
```

### Formato para fine-tuning local

```json
{
  "instruction": "¿Cuál es la fórmula de la energía?",
  "response": "La fórmula de la energía es E=mc², donde E es energía, m es masa y c es la velocidad de la luz."
}
```

## Requisitos

- Para OpenAI: Una cuenta de OpenAI con acceso a la API y créditos suficientes
- Para fine-tuning local: Ollama instalado y configurado
- PostgreSQL con datos de conversaciones almacenados