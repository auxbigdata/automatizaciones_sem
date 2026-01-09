#!/bin/bash

set -e  # Detener si ocurre un error

PYTHON_VERSION="3.10"
VENV_DIR="venv"

echo "?? Verificando Python $PYTHON_VERSION..."

if ! command -v python3.10 &> /dev/null; then
    echo "? Python 3.10 no está instalado"
    echo "?? Instalando Python 3.10..."
    sudo apt update
    sudo apt install -y python3.10 python3.10-venv python3.10-dev
else
    echo "? Python 3.10 encontrado"
fi

echo "?? Versión detectada:"
python3.10 --version

# Crear entorno virtual si no existe
if [ ! -d "$VENV_DIR" ]; then
    echo "?? Creando entorno virtual..."
    python3.10 -m venv $VENV_DIR
else
    echo "?? Entorno virtual ya existe"
fi

echo "?? Activando entorno virtual..."
source $VENV_DIR/bin/activate

echo "?? Actualizando pip..."
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    echo "?? Instalando dependencias..."
    pip install -r requirements.txt
else
    echo "?? requirements.txt no encontrado"
fi

echo "? Instalación finalizada correctamente"
echo "?? Para ejecutar:"
echo "   source venv/bin/activate"
echo "   venv/bin/python main.py"
