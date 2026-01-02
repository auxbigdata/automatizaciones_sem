from ftplib import FTP, error_perm, error_temp
import socket
from datetime import datetime
import os

archivos = []

def conectar_ftp(host: str, puerto: int, user: str, passwd: str):
    """
    Establece y retorna una conexiÃ³n FTP lista para usar.
    """
    ftp = FTP()
    mensaje_conexion = ""
    try:
        ftp.connect(host, puerto, timeout=30)
        ftp.login(user=user, passwd=passwd)
        ftp.set_pasv(True)

        return ftp, f"Conectado exitosamente al FTP {host}:{puerto}"
    except error_perm as e:
        # Errores permanentes (credenciales, permisos)
        mensaje_conexion = f"Error de autenticaciÃ³n(credenciales) FTP: {e}"
    except error_temp as e:
        # Errores temporales del servidor
        mensaje_conexion = f"Error temporal del servidor FTP: {e}"
    except socket.timeout:
        mensaje_conexion = f"Timeout al conectar al servidor FTP"
    except socket.gaierror:
        mensaje_conexion = f"No se pudo resolver el host FTP"
    except Exception as e:
        mensaje_conexion = f"Error inesperado al conectar al FTP {e}"
    # Si algo fallÃ³
    try:
        ftp.quit()
    except Exception:
        pass
    return None, mensaje_conexion

def obtener_archivos_txt(ftp: FTP):
    """Retorna una lista de archivos .txt con su fecha desde el FTP."""
    archivos = []

    def parser(line):
        partes = line.split(maxsplit=8)
        nombre = partes[-1]
        if nombre.lower().endswith(".txt"):
            fecha = " ".join(partes[5:8])
            archivos.append((fecha, nombre))

    ftp.retrlines("LIST", parser)
    return archivos

def obtener_nombre_archivo():
    dia_actual = datetime.now().strftime('%d')
    mes_actual = datetime.now().strftime('%m')
    anio_actual = datetime.now().strftime('%y')

    nombre_archivo = f"RCONL_090_{anio_actual}{mes_actual}{dia_actual}.txt"
    return nombre_archivo

def descargar_archivo(ftp: FTP, nombre_archivo: str, ruta_descarga: str, log) -> bool:
    """Busca y descarga el archivo especificado en el ftp. Retorna True si lo logra."""
    
    archivos = obtener_archivos_txt(ftp)
    ultimos_5 = archivos[-5:]

    os.makedirs(ruta_descarga, exist_ok=True)
    ruta_archivo = os.path.join(ruta_descarga, nombre_archivo)

    log.info("ultimos 5 archivos:")
    for fecha, nombre in ultimos_5:
        log.info(f"{fecha} -> {nombre}")
        if nombre == nombre_archivo:
            log.info(f"Archivo encontrado: {nombre}")

            with open(ruta_archivo, 'wb') as f:
                try:
                    ftp.retrbinary(f"RETR {nombre}", f.write)
                except TimeoutError:
                    log.error("Timeout al descargar archivo desde FTP")
                    return False, None, "Timeout al descargar archivo"
            return True, ruta_archivo,f"Archivo {nombre} descargado correctamente."        
    log.error("El archivo no se encontró en los ultimos 5 registros.")
    return False, None, "Archivo no encontrado en el FTP"
