from src.settings.paths import robot_archivos
from src.settings.config import parametrizar_logs_y_ruta_archivos
from src.settings.config import get_logger
from src.services.servicios_ftp import descargar_archivo, obtener_nombre_archivo, conectar_ftp
from src.services.servicios_email import descargar_adjuntos_por_asunto
from src.services.servicios_sgc import subir_facturacion
import os
import re

robot = "emsa"
log, ruta_descarga = parametrizar_logs_y_ruta_archivos(robot)

# Parametros de correo a buscar
correo="auxbigdata@gmail.com"
pass_aplicacion="mpclkdbfgfqanxvd"
asunto_buscar="Archivos Recaudos Ciclos"
server_imap="imap.gmail.com"
etiqueta_destino=False
# etiqueta_destino="Banco Bogota"

def main():
    log.info("SE INICIA EL PROCESO DE EMSA")
    ruta_archivo, mensaje, nombre_archivo = descargar_adjuntos_por_asunto(email_user=correo,asunto_buscado=asunto_buscar,carpeta_descarga=ruta_descarga,imap_server=server_imap,email_password=pass_aplicacion, etiqueta_correo=etiqueta_destino)

    if not ruta_archivo:
        log.info(mensaje)
        # mandar correo de error

    log.info(mensaje)
    log.info(nombre_archivo)
    log.info(ruta_archivo)
    log.info("Se procede a realizar la peticion al sgc")
    # response = subir_facturacion(nombre_archivo)
if __name__ == "__main__":
    main()