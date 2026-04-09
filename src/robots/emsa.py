from src.settings.config import parametrizar_logs_y_ruta_archivos
from src.services.servicios_email import leer_correos_sin_leer, enviar_email
from src.services.servicios_sgc import subir_facturacion
import re
from src.settings.entorno import env

robot = "emsa"
log, ruta_descarga = parametrizar_logs_y_ruta_archivos(robot)

if env.ENV == "dev":
    prefijo = "PRUEBAS"
else:
    prefijo = ""

# Parametros de correo a buscar
correo="auxbigdata@gmail.com"
pass_aplicacion="mpclkdbfgfqanxvd"
asunto_buscar="Archivos Recaudos Ciclo"
# asunto_buscar = f'SUBJECT "{asunto_buscar}"'
server_imap="imap.gmail.com"
etiqueta_destino="emsa"
# etiqueta_destino="Banco Bogota"

# enviar correo A:
destinatarios =[
    "auxanalista@consuerte.com.co","auxsenadesarrollo@consuerte.com.co"
]

asunto = f"{prefijo} EJECUCIÓN PROCESO EMSA ESPECIAL"
titulo_mensaje = f"{prefijo} ROBOT EMSA ESPECIAL"
mensaje = "Se notifica la ejecución del proceso automatico de emsa especial:<br><br>"


id_tercero = 8
URL = env.URL_SGC

def main():
    log.info("SE INICIA EL PROCESO DE EMSA")
    # ruta_archivo, mensaje, nombre_archivo = descargar_adjuntos_por_asunto(email_user=correo,asunto_buscado=asunto_buscar,carpeta_descarga=ruta_descarga,imap_server=server_imap,email_password=pass_aplicacion, etiqueta_correo=etiqueta_destino, log=log)
    
    ruta_archivo, mensaje_respuesta, nombre_archivos = leer_correos_sin_leer(email_user=correo,asunto_buscado=asunto_buscar,carpeta_descarga=ruta_descarga,imap_server=server_imap,email_password=pass_aplicacion, etiqueta_correo=etiqueta_destino, log=log)

    if not ruta_archivo:
        log.info(mensaje_respuesta)
        enviar_email(
            destinatario=destinatarios,
            mensaje=f"{mensaje}{mensaje_respuesta}",
            asunto=asunto,
            titulo_mensaje="SIN CORREOS EMSA",
            prioridad=1            
        )
        return
    
    log.info(mensaje_respuesta)
    log.info(nombre_archivos)
    log.info(ruta_archivo)
    
    log.info("Se procede a realizar la peticion al sgc")
    URL_UPLOAD = f"{URL}/upload.php"
    log.info(URL_UPLOAD)


    log.info(type(mensaje_respuesta))
    log.info(type(nombre_archivos))
    log.info(type(ruta_archivo))
    
    index = 0 
    log.info(f"cantidad de archivos descargados: {len(nombre_archivos)}")
    for nombre_archivo in nombre_archivos:
        log.info(nombre_archivo)
        log.info(ruta_archivo[index])

        response = subir_facturacion(id_tercero=id_tercero, ruta_archivo=ruta_archivo[index],nombre_archivo=nombre_archivo,URL_UPLOAD=URL_UPLOAD, log=log)

        log.info(f"RESPUESTA DE LA PETICION {index+1}: {response.text}")
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
                adjuntos=ruta_archivo[index]
            )
        index+=1
    # nombre_archivo = nombre_archivo[0]
    # ruta_archivo = ruta_archivo[0]
    # response = subir_facturacion(nombre_archivo)
if __name__ == "__main__":
    main()