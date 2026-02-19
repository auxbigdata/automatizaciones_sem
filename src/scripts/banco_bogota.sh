# PROJECT_DIR="/root/automatizaciones_sem"
# PYTHON_BIN="$PROJECT_DIR/env/bin/python3"

# cd $PROJECT_DIR
# $PYTHON_BIN -m src.robots.banco_bogota
# # /home/ubuntu/python/automatizaciones_sem/env/bin/python3
# 1. Definimos las rutas posibles
PROD_PATH="/root/automatizaciones_sem"
PRUEBAS_PATH="/home/ubuntu/python/automatizaciones_sem"

# 2. El script pregunta: ¿Existe la carpeta de producción?
if [ -d "$PROD_PATH" ]; then
    PROJECT_DIR="$PROD_PATH"
    echo "Entorno detectado: PRODUCCIÓN"
else
    PROJECT_DIR="$PRUEBAS_PATH"
    echo "Entorno detectado: PRUEBAS"
fi

# 3. Configuramos el resto usando la variable detectada
PYTHON_BIN="$PROJECT_DIR/env/bin/python3"

# 4. Ejecución
cd "$PROJECT_DIR"
$PYTHON_BIN -m src.robots.banco_bogota