# 1. AL CLONAR EL PROYECYO LO PRIMERO QUE DEBEMOS HACER ES CREAR EL ENTORNO VIRTUAL (ENV) - LINUX

- nos pedira instalar el paquete de venv para linux: apt install python3.10-venv -y

# CREAR ENTORNO VIRTUAL:
python3 -m venv env

# ACTIVAR ENTORNO VIRTUAL:
source env/bin/activate

# INSTALAR LIBRERIAS DENTRO DEL ENTORNO VIRTUAL:
pip3 install -r requeriments.txt

# INSTALAR NAVEGADORES DE PLAYWRIGHT:
playwright install

# GENERAR ARCHIVO REQUIREMENTS.TXT PARA ACTUALIZAR LAS LIBRERIAS SI SE INSTALA UNA NUEVA:
pip freeze > requirements.txt


# COMANDO PARA EJECUTAR PROCESOS:

python3 -m src.robots.whatsapp_web.app   
python3 -m src.robots.punto_red.app  

 - Podremos acceder a los archivos principales de ejecucion
   como si fueran paquetes y no carpetas.

# COMANDO PARA DAR PERMISOS A LOS .SH:
- ej: 
  chmod +x src/scripts/banco_bogota.sh
