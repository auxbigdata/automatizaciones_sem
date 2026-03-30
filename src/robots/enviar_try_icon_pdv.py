from src.settings.config import parametrizar_logs_y_ruta_archivos
from src.services.servicios_ssh import conexion_sh, comandos_ssh
from src.settings.entorno import env
import pandas as pd
import os

robot = "enviar_try_icon_pdv"
log, ruta_descarga =parametrizar_logs_y_ruta_archivos(robot)

if env.ENV == "dev":
    prefijo = "PRUEBAS"
else:
    prefijo = ""


# comandos = {
#     "DESCOMPRIMIR ARCHIVO" : f"cd {ruta_remota} && tar -xvf {nombre_archivo}",
#     "INGRESAR A CARPETA Y DAR PERMISOS A LOS EJECUTABLES" : f"cd {ruta_carpeta_descomprimida} && chmod +x {ejecutables[0]} {ejecutables[1]}",
#     F"EJECUTAR SCRIPT: {ejecutables[0]}": f"{comando_ejecutar_arregloprinter}",
#     F"EJECUTAR SCRIPT: {ejecutables[1]}": f"{comando_ejecutar_crearcarpeta}",
#     "VERIFICAR CARPETAS": "test -d /home/gamble/superflex && echo 'OK: superflex existe' || echo 'ERROR: superflex no existe'\ntest -d /home/gamble/superflex/Actualizaciones && echo 'OK: Actualizaciones existe' || echo 'ERROR: Actualizaciones no existe'\ntest -d /home/gamble/Documentos/Try_icon && echo 'OK: Try_icon existe' || echo 'ERROR: Try_icon no existe'"
#     }

# comandos = {
#     "INGRESAR A CARPETA" : f"cd {ruta_remota} && tar -xvf {nombre_archivo}",
#     "INGRESAR A CARPETA Y DAR PERMISOS A LOS EJECUTABLES" : f"cd {ruta_carpeta_descomprimida} && chmod +x {ejecutables[0]} {ejecutables[1]}",
#     F"EJECUTAR SCRIPT: {ejecutables[0]}": f"{comando_ejecutar_arregloprinter}",
#     F"EJECUTAR SCRIPT: {ejecutables[1]}": f"{comando_ejecutar_crearcarpeta}",
#     "VERIFICAR CARPETAS": "test -d /home/gamble/superflex && echo 'OK: superflex existe' || echo 'ERROR: superflex no existe'\ntest -d /home/gamble/superflex/Actualizaciones && echo 'OK: Actualizaciones existe' || echo 'ERROR: Actualizaciones no existe'\ntest -d /home/gamble/Documentos/Try_icon && echo 'OK: Try_icon existe' || echo 'ERROR: Try_icon no existe'"
#     }

def main():
    log.info("SE INICIA EL PROCESO DE ENVIAR EL TRY ICON A TODOS LOS PDV")

    ip = "10.2.12.146"
    ip = "10.8.0.231"

    host = ip
    port = 22
    username = 'gamble'
    password = 'consuerte'

    # ruta_archivo_local = ""
    ruta_destino_try_icon = "/home/gamble/Documentos/Try_icon"
    ruta_archivo_local = os.path.join(ruta_descarga, "superflex-tray-icon.jar")

    comandos = {
        "INGRESAR A CARPETA" : f"cd {ruta_destino_try_icon}",
        "ENVIAR TRY ICON A PDV" : f"scp {ruta_archivo_local} {username}@{ip}:{ruta_destino_try_icon}",
        # "INGRESAR A CARPETA" : f"cd {ruta_remota} && tar -xvf {nombre_archivo}",
        # "INGRESAR A CARPETA Y DAR PERMISOS A LOS EJECUTABLES" : f"cd {ruta_carpeta_descomprimida} && chmod +x {ejecutables[0]} {ejecutables[1]}",
        # F"EJECUTAR SCRIPT: {ejecutables[0]}": f"{comando_ejecutar_arregloprinter}",
        # F"EJECUTAR SCRIPT: {ejecutables[1]}": f"{comando_ejecutar_crearcarpeta}",
        # "VERIFICAR CARPETAS": "test -d /home/gamble/superflex && echo 'OK: superflex existe' || echo 'ERROR: superflex no existe'\ntest -d /home/gamble/superflex/Actualizaciones && echo 'OK: Actualizaciones existe' || echo 'ERROR: Actualizaciones no existe'\ntest -d /home/gamble/Documentos/Try_icon && echo 'OK: Try_icon existe' || echo 'ERROR: Try_icon no existe'"
    }

    # leer excel
    # ruta_excel = f"{ruta_descarga}/puntos5.xlsx"
    nombre_excel = "puntos5.xlsx"
    ruta_excel = os.path.join(ruta_descarga, nombre_excel)

    log.info("se ingresa a leer el excel")
    df = pd.read_excel(ruta_excel)

    for index, row in df.iterrows():
        ip = row['IP']
        log.info("-------------------------")
        log.info(f"iterando ip: {ip}")
        ip = "10.2.12.82"
        ip = "10.255.2.136"
        ip = "10.2.10.144"
        ip = "10.2.10.105"
        client = conexion_sh(ip=ip,log=log,password=password,puerto=port,username=username)

        if not client:
            log.info("Fallo al conectarse al host")
            return

        comandos_ssh(log=log, client=client,comandos=comandos)


        log.info("-------------------------")

if __name__ == "__main__":
    main()