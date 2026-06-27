from src.settings.entorno import env
from src.settings.config import parametrizar_logs_y_ruta_archivos
from src.services.servicios_email import enviar_email
from src.services.servicios_filezila import conexion_filezilla,descargar_archivos_sftp,unificar_archivos,obtener_ruta_remota


robot = "kenno"
log, ruta_descarga = parametrizar_logs_y_ruta_archivos(robot)

if env.ENV == "dev":
    prefijo = ""
else:
    prefijo = ""   

# enviar correo A:
destinatarios =[
    "auxanalista@consuerte.com.co",
    "asiscontab2@consuerte.com.co"
]

asunto = f"{prefijo} EJECUCIÓN PROCESO KENNO"
titulo_mensaje = f"{prefijo} ROBOT KENNO"
mensaje = "Se notifica la ejecución del proceso automatico de kenno:<br><br>"

def main():
    log.info("SE INICIA EL PROCESO DE KENNO")

    # credenciales de filezilla
    host = "112.14.45.243"
    puerto = 5122
    usuario = "asiscontab2"
    password = "358lw4aDUUK5"

    # 1. CONEXIÓN (Recibimos las 4 variables aquí)
    conexion_exitosa, ssh_client, sftp, mensaje_error = conexion_filezilla(host, puerto, usuario, password, log)
    if not conexion_exitosa:
        enviar_email(
            destinatario=destinatarios,
            mensaje=f"{mensaje}{mensaje_error}",
            asunto=f"ERORR {asunto}",
            titulo_mensaje=titulo_mensaje,
            prioridad=1)
        return

    log.info("Conexión establecida")


    ruta_a_explorar, mensaje_error = obtener_ruta_remota(log=log)

    if ruta_a_explorar is None:
        enviar_email(
            destinatario=destinatarios,
            mensaje=f"{mensaje}Error al obtener la ruta remota: {mensaje_error}",
            asunto=f"ERROR {asunto}",
            titulo_mensaje=titulo_mensaje,
            prioridad=1)
        return
    
    # llamamos a la funcion descarga_archivos_sftp
    lista_archvios, error_descarga = descargar_archivos_sftp(sftp = sftp, ruta_directorio=ruta_a_explorar,ruta_descarga=ruta_descarga,log = log)

    if lista_archvios is None:
        enviar_email(
            destinatario=destinatarios,
            mensaje=f"{mensaje}Error al descargar archivos: {error_descarga}",
            asunto=f"ERROR {asunto}",
            titulo_mensaje=titulo_mensaje,
            prioridad=1)
        return
    log.info(f"Archivos descargados")

    # llamamos a la funcion unificar_archivos
    ruta_archivo_final, error_unificacion = unificar_archivos(lista_archivos=lista_archvios, ruta_a_explorar=ruta_a_explorar,ruta_descarga=ruta_descarga,log=log)

    if ruta_archivo_final is None:
        enviar_email(
            destinatario=destinatarios,
            mensaje=f"{mensaje}Error al unificar archivos: {error_unificacion}",
            asunto=f"ERROR {asunto}",
            titulo_mensaje=titulo_mensaje,
            prioridad=1)
        return
    log.info(f"Archivos unificados exitosamente.")

    log.info("enviando correo con archivo adjunto")
    enviar_email(
        destinatario=destinatarios,
        mensaje=f"{mensaje}<br><br>se envia el consolidado de kenno del dia {ruta_a_explorar}",
        asunto=f"{asunto}",
        titulo_mensaje=titulo_mensaje,
        adjuntos=ruta_archivo_final
    )


if __name__ == "__main__":
    main()