from src.services.utils import obtener_fecha_ayer
from src.settings.config import parametrizar_logs_y_ruta_archivos
from src.services.servicios_email import enviar_email
from src.services.servicios_sgc import subir_archivo_cofres_inteligentes
from src.services.servicios_peticiones import iniciar_sesion_brinks, descargar_reporte_brinks
from src.settings.entorno import env

robot = "cofres_inteligentes"
log, ruta_descarga = parametrizar_logs_y_ruta_archivos(robot)

if env.ENV == "dev":
    prefijo = "PRUEBAS"
else:
    prefijo = ""

destinatarios = [
    "auxanalista@consuerte.com.co",
    "auxsenadesarrollo@consuerte.com.co"
]

asunto = f"{prefijo} EJECUCIÓN PROCESO COFRES_INTELIGENTES"
titulo_mensaje = f"{prefijo} ROBOT COFRES INTELIGENTES"
mensaje = "Se notifica la ejecución del proceso automatico de Cofres inteligentes: "

URL_SUBIR_ARCHIVO = env.URL_SGC_SUBIR_ARCHIVO_COFRES

def main():
    global mensaje

    session, response = iniciar_sesion_brinks(log)

    if session is False and type(response) == str:
        log.error(response)
        enviar_email(
            destinatario=destinatarios,
            asunto=f"ERROR {asunto}",
            mensaje=f"{mensaje}{response}",
            titulo_mensaje=titulo_mensaje,
            prioridad=1
        )
        return

    if not session.user_id:
        respuesta = "No se logró iniciar sesión, no se obtuvo un usuario válido."
        log.error(respuesta)
        enviar_email(
            destinatario=destinatarios,
            asunto=f"ERROR {asunto}",
            mensaje=f"{mensaje}{respuesta}",
            titulo_mensaje=titulo_mensaje,
            prioridad=1
        )
        return

    log.info(f"Usuario Autenticado: {session.user_id}")

    log.info("Iniciando descarga del reporte")
    ruta_archivo, mensaje_descarga, nombre_archivo = descargar_reporte_brinks(
        session=session,
        ruta_descargas=ruta_descarga,
        log=log
    )

    if ruta_archivo is None:
        log.error(mensaje_descarga)
        enviar_email(
            destinatario=destinatarios,
            asunto=f"ERROR {asunto}",
            mensaje=f"{mensaje}{mensaje_descarga}",
            titulo_mensaje=titulo_mensaje,
            prioridad=1
        )
        return

    log.info(mensaje_descarga)
    log.info(ruta_archivo)

    response = subir_archivo_cofres_inteligentes(
        ruta_archivo=ruta_archivo,
        log=log,
        URL=URL_SUBIR_ARCHIVO
    )

    log.info(f"RESPUESTA DE LA PETICIÓN: {response.text}")
    
    try:
        respuesta_json = response.json()
        mensaje_subida = respuesta_json[0].get("message", "Proceso completado.")
        status = respuesta_json[0].get("status")

        if status == 1:
            log.info(f"STATUS_CODE: {response.status_code}")
            log.info(mensaje_subida)
            enviar_email(
                destinatario=destinatarios,
                asunto=asunto,
                mensaje=f"{mensaje_subida}<br><br>Nombre Archivo: {nombre_archivo}",
                titulo_mensaje=titulo_mensaje,
                adjuntos=ruta_archivo
            )
        else:
            log.error(f"Error al subir archivo: {mensaje_subida}")
            enviar_email(
                destinatario=destinatarios,
                asunto=f"ERROR {asunto}",
                mensaje=f"{mensaje}{mensaje_subida}",
                titulo_mensaje=titulo_mensaje,
                prioridad=1
            )
    except Exception as e:
        log.error(f"Error procesando respuesta del backend: {e}")

if __name__ == "__main__":
    main()
