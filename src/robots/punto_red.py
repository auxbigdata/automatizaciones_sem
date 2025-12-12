# from src.functions.browser import open_browser
# from src.functions.login_sgc import iniciar_sesion_sgc
# from src.functions.utils import subir_facturacion
# from src.functions.subir_archivo_sgc import subir_archivo_sgc
from src.services.request_conciliacion import request_conciliacion
from src.settings.paths import robot_archivos
from src.settings.config import get_logger
from src.services.servicios_ftp import descargar_archivo, obtener_nombre_archivo, conectar_ftp
import os
import re

log = get_logger("punto_red")

def main():
    # Configuraciones iniciales
    BASE_DIR = os.path.dirname(__file__)
    USER = "CP1029980182"
    PASS = "123"
    URL = "http://10.1.1.11/consuertepruebas"
    # URL = "http://10.1.1.4/consuerteinventarios"
    URL_HOME = f"{URL}/start.php"
    tercero = "830513238 - CONEX RED-PUNTO RED"

    #CONEXION FTP Y DESCARGA ARCHIVO
    host = '10.8.0.23'
    puerto = 2121
    user = 'traeconsuerte'
    password = '800159687'
    ftp = conectar_ftp(host, puerto, user, password, log)
    # ruta_descarga = os.path.join(BASE_DIR, 'archivos_punto_red')
    ruta_descarga = robot_archivos("punto_red")

    log.info("Hola")

    nombre_archivo = obtener_nombre_archivo(log)
    exito, ruta_archivo = descargar_archivo(ftp, nombre_archivo, ruta_descarga, log)
    
    if exito:
        log.info("Archivo descargado exitosamente.")
        log.info(ruta_archivo)
        #INICIO SESION SGC Y SUBIDA FACTURACION
        # page = open_browser(headless=False)
        # iniciar_sesion_sgc(page, URL, URL_HOME, PASS, USER)
        # subir_facturacion(page, URL, tercero)
        # subir_archivo_sgc(page, ruta_archivo)
        # input("asd")
        data = {
            "usuario": "CP1029980182",
            "tiemposesion": "1763499600887",
            "estadotiempo": "0",
            "comodin": "1",
            "como": "0",
            "tercero": "495",
            "tipore2": "1",
            "tipore3": "1",
            "tipore26": "1",
            "tipore4": "1",
            "tipore": "0",
            "cantidad_1": "0",
            "submitBtn": "Subir"
        }
        URL_UPLOAD = f"{URL}/upload.php"
        log.info(URL_UPLOAD)
        response = request_conciliacion(data,ruta_archivo,nombre_archivo, URL_UPLOAD, log)
        log.info(f"RESPUESTA DE LA PETICION: {response.text}")
        m = re.search(r"stopUpload\(\s*\d+\s*,\s*'(.*?)'", response.text)
        if m:
            mensaje = m.group(1)
            log.info(f"STATUS_CODE: {response.status_code}")
            log.info(mensaje)
        # print("Respuesta del servidor de conciliaciÃƒÆ’Ã‚Â³n recibida." + response)
    else: 
        log.error("No se pudo descargar el archivo. Proceso detenido.")
    ftp.quit()

    
if __name__ == "__main__":
    main()