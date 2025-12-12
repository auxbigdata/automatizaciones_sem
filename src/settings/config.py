URL = "http://10.1.1.11/consuertepruebas"
import logging
import os
from datetime import datetime

# Carpeta raíz del proyecto
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def get_logger(robot_name: str):
    # Crea un logger para un robot específico.
    # Cada ejecución genera un archivo .log con fecha y hora.
    

    # Carpeta donde se guardarán los logs del robot
    LOGS_DIR = os.path.join(BASE_DIR, "resources", robot_name, "logs")
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Nombre dinámico del archivo
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(LOGS_DIR, f"{timestamp}.log")

    # Crear logger único por robot
    logger = logging.getLogger(f"{robot_name}_logger")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler para archivo
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Evitar duplicados
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger