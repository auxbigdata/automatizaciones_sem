from datetime import datetime, timedelta
import smbclient
import smbclient.shutil

def obtener_fecha_ayer():
    ayer = datetime.now() - timedelta(days=1)
    return ayer.strftime("%Y/%m/%d")

def obtener_fecha_actual():
    ahora = datetime.now()
    return ahora.strftime("%Y-%m-%d")

def conectar_a_carpeta_compartida(servidor: str, usuario: str, contraseña: str, log: object):
    try:
        smbclient.register_session(servidor, username=usuario, password=contraseña)
        log.info(f"Conexión exitosa a la carpeta compartida {servidor}")
        return True
    except Exception as e:
        log.error(f"Error al conectar a la carpeta compartida {servidor}: {e}")
        return False

def verificar_carpeta_destino(carpeta_destino: str, log: object):
    try:
        if not smbclient.path.isdir(carpeta_destino):
            log.error(f"La carpeta destino no existe en la compartida: {carpeta_destino}")
            smbclient.makedirs(carpeta_destino, exist_ok=True)
            log.info(f"Carpeta creada exitosamente: {carpeta_destino}")
        else:
            log.info(f"La carpeta destino se encuentra en la compartida: {carpeta_destino}")
        log.info(f"Se continua el proceso")
        return True

    except Exception as e:
        log.error(f"Error al verificar o crear la carpeta destino {carpeta_destino}: {e}")
        return False