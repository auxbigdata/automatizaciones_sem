from src.settings.paths import robot_archivos
from src.settings.config import parametrizar_logs_y_ruta_archivos
from src.settings.config import get_logger
from src.services.servicios_ftp import descargar_archivo, obtener_nombre_archivo, conectar_ftp
from src.services.servicios_email import descargar_adjuntos_por_asunto, enviar_email
from src.services.servicios_sgc import subir_facturacion
import os
import re

robot = "banco_bogota"
log, ruta_descarga = parametrizar_logs_y_ruta_archivos(robot)

# Parametros de correo a buscar
correo="auxbigdata@gmail.com"
pass_aplicacion="mpclkdbfgfqanxvd"
asunto_buscar="Archivos SIC Redeban Multicolor S.A."
server_imap="imap.gmail.com"
etiqueta_destino="Banco Bogota"

# enviar correo A:
destinatarios =[
    "auxanalista@consuerte.com.co",
    "asis_desarrollo@consuerte.com.co"
]
asunto = "EJECUCIÓN PROCESO BANCO BOGOTA"
titulo_mensaje = "PRUEBAS ROBOT BANCO BOGOTA"
mensaje = "Se notifica la ejecución del proceso automatico de banco bogota:<br><br>"

# PARAMETROS DE PETICION AL SGC
id_tercero = 76 # 860002964 - BANCO DE BOGOTA 
URL = "http://10.1.1.11/consuertepruebas"

def main():
    log.info("SE INICIA EL PROCESO DE BANCO BOGOTA")

    ruta_archivo, mensaje_respuesta, nombre_archivo = descargar_adjuntos_por_asunto(email_user=correo,asunto_buscado=asunto_buscar,carpeta_descarga=ruta_descarga,imap_server=server_imap,email_password=pass_aplicacion, etiqueta_correo=etiqueta_destino, log=log)

    if not ruta_archivo:
        log.info(mensaje_respuesta)
        # mandar correo de error
        enviar_email(
            destinatario=destinatarios,
            mensaje=f"{mensaje}{mensaje_respuesta}",
            asunto=f"ERROR {asunto}",
            titulo_mensaje=titulo_mensaje,
            prioridad=1
        )
        return
    
    if len(ruta_archivo) == 1:
        log.info(f"Cantidad de archivos descargados: {len(ruta_archivo)}")
        nombre_archivo = nombre_archivo[0]
        ruta_archivo = ruta_archivo[0] # elemento de la lista pasado a string
    else:
        log.error("SE ENCONTRÓ MAS DE UN ARCHIVO EL CORREO DE BANCO BOGOTA")
        log.error(nombre_archivo)
        mensaje_respuesta = "Se encontraron mas de un archivo en el correo de banco bogota, por favor revisar esta novedad"
        enviar_email(
            destinatario=destinatarios,
            mensaje=f"{mensaje}{mensaje_respuesta}<br><br>{nombre_archivo}",
            asunto=f"ERROR {asunto}",
            titulo_mensaje=titulo_mensaje,
            prioridad=1,
            adjuntos=ruta_archivo
        )
        return
    log.info(mensaje_respuesta)
    log.info(nombre_archivo)
    log.info(ruta_archivo)
    log.info("Se procede a realizar la peticion al sgc")
    URL_UPLOAD = f"{URL}/upload.php"
    log.info(URL_UPLOAD)

    response = subir_facturacion(id_tercero=id_tercero, ruta_archivo=ruta_archivo,nombre_archivo=nombre_archivo,URL_UPLOAD=URL_UPLOAD, log=log)

    log.info(f"RESPUESTA DE LA PETICION: {response.text}")
    m = re.search(r"stopUpload\(\s*\d+\s*,\s*'(.*?)'", response.text)
    if m:
        respuesta_peticion = m.group(1)
        log.info(f"STATUS_CODE: {response.status_code}")
        log.info(respuesta_peticion)
        enviar_email (
            destinatario=destinatarios,
            asunto=asunto,
            mensaje=f"{mensaje}{respuesta_peticion}.<br><br>Nombre Archivo: {nombre_archivo}",
            titulo_mensaje=titulo_mensaje,
            adjuntos=ruta_archivo
        )

if __name__ == "__main__":
    main()