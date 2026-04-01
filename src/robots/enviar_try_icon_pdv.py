from src.settings.config import parametrizar_logs_y_ruta_archivos
from src.services.servicios_ssh import conexion_sh, comandos_ssh, enviar_archivo
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

    nombre_archivo = "superflex-tray-icon.jar"
    # ruta_archivo_local = ""
    ruta_destino_try_icon = f"/home/gamble/Documentos/Try_icon/{nombre_archivo}"
    # ruta_destino_try_icon = f"/home/gamble/Documentos/prueba_try_icon/{nombre_archivo}"
    # ruta_archivo_local = os.path.join(ruta_descarga, "superflex-tray-icon.jar")
    ruta_archivo_local = fr"{ruta_descarga}\{nombre_archivo}"
    ruta_archivo_local = r'C:\automatizaciones_sem\resources\enviar_try_icon_pdv\archivos\superflex-tray-icon.jar'
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
    nombre_excel = "puntos_procesados.xlsx"
    # nombre_excel = "puntos_procesados - copia.xlsx"
    ruta_excel = os.path.join(ruta_descarga, nombre_excel)

    log.info("se ingresa a leer el excel")
    df = pd.read_excel(ruta_excel)
    con = 3
    for index, row in df.iterrows():
        # if con 
        ip = row['IP']
        estado_archivo = row['ARCHIVO'] 
        log.info("-------------------------")
        log.info(f"iterando ip: {ip}")

        log.info(f"estado_archivo: {estado_archivo}")
        if estado_archivo == True:
            log.info(f"Se valida {estado_archivo} en la celda archivo")
            log.info(f"Se continua el siguiente registro")
            continue
        # ip = "10.2.12.82"
        # ip = "10.255.2.136"
        # ip = "10.2.10.144"
        # ip = "10.2.10.105"
        client = conexion_sh(ip=ip,log=log,password=password,puerto=port,username=username)

        if not client:
            log.info("Fallo al conectarse al host")
            df.at[index, "CONEXION SSH"] = "False"
            continue
        
        df.at[index, "CONEXION SSH"] = "True"
        client.exec_command('sudo mkdir -p /home/gamble/Documentos/Try_icon/')
        client.exec_command('sudo chown -R gamble:gamble /home/gamble/Documentos/Try_icon/')

        if enviar_archivo(log=log,client=client,ruta_local=ruta_archivo_local,ruta_remota=ruta_destino_try_icon):
            df.at[index, "ARCHIVO"] = "True"
            log.info("se envio el archivo correctamente")
        # comandos_ssh(log=log, client=client,comandos=comandos)
        else:
            df.at[index, "ARCHIVO"] = "False"
             
        with pd.ExcelWriter(ruta_excel, engine="openpyxl", mode="w") as writer:
            df.to_excel(writer, index=False)
        log.info("-------------------------")

if __name__ == "__main__":
    main()