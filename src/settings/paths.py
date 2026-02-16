import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
# BASE_DIR = os.path.dirname(__file__)

def robot_archivos(name):
    '''
    Docstring for robot_archivos
    
    :param name: Nombre de la carpeta del robot donde se dejaran los archivos en caso de necesitarlo

    '''

    path = os.path.join(robot_path(name), "archivos")
    os.makedirs(path, exist_ok=True)
    return path

def robot_path(name):
    return os.path.join(BASE_DIR, "resources", name)

def robot_logs(name):
    return os.path.join(robot_path(name), "logs")

