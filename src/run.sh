#!/bin/bash
# Script sencillo para indexar, consultar, iniciar la web y hacer fine-tuning

set -e

case $1 in
  indexar)
    python main.py --index
    ;;
  chat)
    python main.py --chat
    ;;
  web)
    python main.py --web
    ;;
  fine-tuning)
    python main.py --fine-tune --provider local
    ;;
  fine-tuning-openai)
    python main.py --fine-tune --provider openai
    ;;
  *)
    echo "Uso: $0 {indexar|chat|web|fine-tuning|fine-tuning-openai}"
    exit 1
    ;;
esac
