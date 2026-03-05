from src.services.utils import obtener_fecha_ayer
from src.settings.config import parametrizar_logs_y_ruta_archivos
from src.services.servicios_email import enviar_email
from src.services.servicios_sgc import subir_facturacion
from src.services.servicios_peticiones import iniciar_sesion, descargar_reporte
from src.settings.entorno import env
from pathlib import Path
import re
robot = "cofrem"
log,ruta_descarga = parametrizar_logs_y_ruta_archivos(robot)

if env.ENV == "dev":
    prefijo = "PRUEBAS"
else:
    prefijo = ""

# Parametros SGC
id_tercero = 50
URL = env.URL_SGC
URL_UPLOAD = f"{URL}/upload.php"

# parametros enviar correo
destinatarios = [
    "auxanalista@consuerte.com.co",
    "auxsenadesarrollo@consuerte.com.co"
]

asunto = f"{prefijo} EJECUCIÓN PROCESO COFREM"
titulo_mensaje = f"{prefijo} ROBOT COFREM"
mensaje = "Se notifica la ejecucion del proceso automatico de cofrem:<br><br>"

# Passwor y user de cofrem
USER = env.USER_COFREM
PASS = env.PASS_COFREM
URL_HOME_COFREM = env.URL_HOME_COFREM
URL_LOGIN_COFREM = env.URL_LOGIN_COFREM
URL_REPORTE = env.URL_REPORTE_COFREM

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/x-www-form-urlencoded"
}

payload = {
    'id_usuario': USER,
    'pwd_usuario': PASS
}

def main():
    global mensaje
    
    session, response = iniciar_sesion(url=URL_LOGIN_COFREM, headers=headers, payload=payload, log=log)

    if session is False and type(response) == str:
        log.error(response)
        enviar_email(destinatario=destinatarios,
            asunto=f"ERROR {asunto}", 
            mensaje=f"{mensaje}{response}", 
            titulo_mensaje=titulo_mensaje, 
            prioridad=1
        )
        return

    if response.url != URL_HOME_COFREM:
        respuesta = f"No se logró iniciar sesión, la URL obtenida no es la correcta: <br><br> {response.url}"
        log.error(respuesta)
        log.error(f"session: {session}")
        enviar_email(destinatario=destinatarios,
            asunto=f"ERROR {asunto}", 
            mensaje=f"{mensaje}{respuesta}", 
            titulo_mensaje=titulo_mensaje, 
            prioridad=1
        )
        return
    
    log.info(f"URL obtenida: {response.url}")

    # configuracion fecha 
    fecha = obtener_fecha_ayer()

    log.info(f"Fecha consultada: {fecha}")

    payload_descarga = {
        'fecini': fecha,
        'fecfin': fecha
    }

    # Descarga reporte cofrem
    log.info("Iniciando descarga del reporte")
    ruta_archivo, mensaje_descarga, nombre_archivo = descargar_reporte(session=session, url=URL_REPORTE, headers=headers, payload=payload_descarga, ruta_descarga=ruta_descarga, log=log)

    if ruta_archivo is None:
        log.info(mensaje_descarga)
        enviar_email(destinatario=destinatarios,
            asunto=f"ERROR {asunto}", 
            mensaje=f"{mensaje}{mensaje_descarga}", 
            titulo_mensaje=titulo_mensaje, 
            prioridad=1
        )
        return
    log.info(mensaje_descarga)
    log.info(ruta_archivo)

    
    response = subir_facturacion(id_tercero=id_tercero, ruta_archivo=ruta_archivo,nombre_archivo=nombre_archivo,log=log,URL_UPLOAD=URL_UPLOAD)
    log.info(f"RESPUESTA DE LA PETICION: {response.text}")
    m = re.search(r"stopUpload\(\s*\d+\s*,\s*'(.*?)'", response.text)
    if m:
        mensaje = m.group(1)
        log.info(f"STATUS_CODE: {response.status_code}")
        log.info(mensaje)
        enviar_email (
            destinatario=destinatarios,
            asunto=asunto,
            mensaje=f"{mensaje}<br><br>Nombre Archivo: {nombre_archivo}",
            titulo_mensaje=titulo_mensaje,
            adjuntos=ruta_archivo
        )
if __name__ == "__main__":
    main()