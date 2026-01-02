from src.settings.config import parametrizar_logs_y_ruta_archivos
from src.settings.paths import robot_archivos
from src.settings.config import get_logger
from src.services.servicios_ftp import descargar_archivo, obtener_nombre_archivo, conectar_ftp
from src.services.servicios_email import enviar_email
from src.services.servicios_sgc import subir_facturacion
import os
import re

robot = "punto_red"
log, ruta_descarga =parametrizar_logs_y_ruta_archivos(robot)

# CREDENCIALES CONEXION FTP
host = '10.8.0.23'
puerto = 2121
user = 'traeconsuerte'
password = '800159687'

# PARAMETROS DE PETICION AL SGC
id_tercero = 495 # 830513238 - CONEX RED-PUNTO RED
URL = "http://10.1.1.11/consuertepruebas"

destinatarios=[
    "auxanalista@consuerte.com.co",
    "asis_desarrollo@consuerte.com.co"
]

asunto="EJECUCIÓN PROCESO PUNTO RED"
titulo_mensaje="PRUEBAS ROBOT PUNTO RED"

def main():

    log.info("SE INICIA EL PROCESO DE PUNTO RED")
    ftp, mensaje_conexion = conectar_ftp(host, puerto, user, password)

    if not ftp:
        log.error("No se pudo continuar el proceso")
        log.error(mensaje_conexion)
        enviar_email(
            destinatario=destinatarios,
            mensaje=f"Se notifica la ejecución del proceso automatico de punto red:<br><br>{mensaje_conexion}",
            asunto=asunto,
            titulo_mensaje="ERROR FTP"            
        )
        return
    log.info(mensaje_conexion)
    #obtener nombre de archivo punto red
    nombre_archivo = obtener_nombre_archivo()
    log.info(f"Nombre del archivo a buscar: {nombre_archivo}")

    # descargar archivo
    exito, ruta_archivo, mensaje_descarga_archivo = descargar_archivo(ftp, nombre_archivo, ruta_descarga, log)
    # exito = False
    if exito:
        log.info(mensaje_descarga_archivo)
        log.info(ruta_archivo)
        URL_UPLOAD = f"{URL}/upload.php"
        log.info(URL_UPLOAD)
        
        response = subir_facturacion(id_tercero,ruta_archivo,nombre_archivo, URL_UPLOAD, log)

        log.info(f"RESPUESTA DE LA PETICION: {response.text}")
        m = re.search(r"stopUpload\(\s*\d+\s*,\s*'(.*?)'", response.text)
        if m:
            mensaje = m.group(1)
            log.info(f"STATUS_CODE: {response.status_code}")
            log.info(mensaje)
            enviar_email (
                destinatario=destinatarios,
                asunto=asunto,
                mensaje=f"Se notifica la ejecución del proceso automatico de punto red:<br><br>{mensaje}.<br><br>Nombre Archivo: {nombre_archivo}",
                titulo_mensaje=titulo_mensaje,
                adjuntos=ruta_archivo
            )
    else:
        log.error(mensaje_descarga_archivo) 
        log.error("Ocurrió un error al descargar el archivo. Proceso detenido.")
        enviar_email (
                destinatario=destinatarios,
                asunto=asunto,
                mensaje=f"OcurriÃ³ un error al descargar el archivo: {nombre_archivo} de punto red.<br><br>{mensaje_descarga_archivo}, proceso detenido.",
                titulo_mensaje="FALLO EN ROBOT PUNTO RED"
            )
    ftp.quit()

if __name__ == "__main__":
    main()