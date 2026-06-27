import paramiko
import socket
import pandas as pd
import os
import stat # Para verificar si un elemento es una carpeta o un archivo
from datetime import datetime, timedelta



# funcion  obtener ruta remota
def  obtener_ruta_remota(log: object):
    try:
        # buscamos la fecha 
        fecha_actual = datetime.now() - timedelta(days=1)

        # extraemos año, mes y dia
        año = fecha_actual.strftime("%Y")
        mes = fecha_actual.strftime("%m")
        dia = fecha_actual.strftime("%d")

        # construimos la ruta dinamica
        ruta_remota = f"/upload/bet/{año}/{mes}/{dia}"
        # ruta_remota = f"/upload/bet/2026/06/25" # RUTA PARA DIAS ESPECIFICOS DE PRUEBA
        log.info(f"Ruta remota construida: {ruta_remota}")
        return ruta_remota, None
    except Exception as e:
        mensaje_error = f"Error al construir la ruta remota: {e}"
        log.error(mensaje_error)
        return None, mensaje_error


# Función encargada de establecer la conexión y retornar el canal abierto
def conexion_filezilla(host: str, puerto: int, usuario: str, password: str, log: object):
    try: 
        log.info(f"Iniciando conexión a FileZilla en {host}:{puerto}...")

        # socket.AF_INET: Fuerza el uso de IPv4 (IPs normales) para evitar bloqueos del sistema.
        # socket.SOCK_STREAM: Protocolo TCP, garantiza que la información no se pierda en el viaje.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # El timeout es clave: Si el servidor es lento o está bloqueado, no dejamos al robot colgado.
        sock.settimeout(15) 
        sock.connect((host, puerto))

        ssh_client = paramiko.SSHClient()
        # AutoAddPolicy permite que el robot confíe en el servidor remoto sin pedir confirmación manual.
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Conectamos inyectando el socket ('sock') para forzar la ruta de red que ya probamos.
        ssh_client.connect(hostname=host, port=puerto, username=usuario,password=password,sock=sock)

        # Abrimos el canal SFTP, que es el "transporte" para archivos que vive dentro del túnel SSH.
        sftp = ssh_client.open_sftp()
        log.info("Conexión a FileZilla establecida exitosamente.")
        
        # Retornamos los objetos necesarios para que el robot pueda trabajar con ellos.
        return True, ssh_client, sftp, "Conexión exitosa"

    except Exception as e:
        mensaje_error = f"Error al conectar: {e}"
        log.error(mensaje_error)
        # Si falla, devolvemos None en los objetos para que el main sepa que no hay nada que cerrar.
        return False, None, None, mensaje_error


# Función que usa el canal sftp ya abierto para listar el contenido
def obtener_contenido_directorio(sftp: object, ruta_directorio: str, log: object):
    try:
        log.info(f"Obteniendo contenido del directorio: {ruta_directorio}")
        
        # listdir_attr lee los metadatos (tipo de archivo, permisos, etc.)
        elementos = sftp.listdir_attr(ruta_directorio)
        
        carpetas = []
        archivos = []

        for elemento in elementos:
            # stat.S_ISDIR filtra los elementos: si es carpeta (True), va a la lista de carpetas.
            if stat.S_ISDIR(elemento.st_mode):
                carpetas.append(elemento.filename)
            else:
                archivos.append(elemento.filename)
                
        return carpetas, archivos, "Lectura de carpetas exitosa."

    except Exception as e:
        mensaje_error = f"Error al intentar leer la ruta '{ruta_directorio}': {e}"
        log.error(mensaje_error)
        # Retornamos None, None para que tu lógica de validación (if carpetas is None) funcione igual que en cofrem.py
        return None, None, mensaje_error
    
def descargar_archivos_sftp(sftp: object, ruta_directorio: str, ruta_descarga: str, log: object):
    try:
        log.info(f"iniciando descarga de archivos")

        # extrameos las partesd e la ruta remota
        partes_ruta = ruta_directorio.strip('/').split('/')

        # tomamos mes y dia 
        mes =partes_ruta[-2]
        dia = partes_ruta[-1]

        # Unimos tu ruta_descarga base con la carpeta extraída
        ruta_destino_final = os.path.join(ruta_descarga, mes,dia)

        # validamos si la carpeta existe, si no, la creamos
        if not os.path.exists(ruta_destino_final):
            os.makedirs(ruta_destino_final)
            log.info(f"Carpeta creada en el equipo: {ruta_destino_final}")

        # Leemos el directorio del servidor
        elementos = sftp.listdir_attr(ruta_directorio)
        archivos_descargados = []

        for elemento in elementos:
            # validamos que sea archvio y no carpeta
            if not stat.S_ISDIR(elemento.st_mode):
                nombre_archivo = elemento.filename
                # ruta origen del servidor
                ruta_origen = f"{ruta_directorio}/{nombre_archivo}"
                # ruta destino en el equipo local
                ruta_archivo_local = os.path.join(ruta_destino_final, nombre_archivo)
                # descargamos el archivo
                sftp.get(ruta_origen, ruta_archivo_local)
                archivos_descargados.append(ruta_archivo_local)
                
        if not archivos_descargados:
            mensaje_error = f"La carpeta remota {ruta_directorio} está vacía."
            log.error(mensaje_error)
            return None, mensaje_error
        # Retorno exitoso
        return archivos_descargados, None
        
    except Exception as e:
        mensaje_error = f"Error inesperado al descargar la ruta {ruta_directorio}: {e}"
        log.error(mensaje_error)
        return None, mensaje_error

def unificar_archivos(lista_archivos: list, ruta_a_explorar: str, ruta_descarga: str, log: object):

    try:
        # Extraemos el nombre de la carpeta
        partes_ruta = ruta_a_explorar.strip('/').split('/')
        # Construimos la ruta local
        # Obtenemos mes y día
        mes = partes_ruta[-2]
        dia = partes_ruta[-1]
        # Construimos la ruta correcta:
        ruta_carpeta_local = os.path.join(ruta_descarga, mes, dia)
        # Nombre del archivo consolidado
        nombre_consolidado = f"Consolidado_Datos_{mes}_{dia}.csv"
        # Ruta final del consolidado
        ruta_consolidado = os.path.join(ruta_carpeta_local, nombre_consolidado)
        log.info("Iniciando unificación de archivos CSV")

        encabezado_guardado = False

        # Abrimos el archivo final en modo escritura
        with open(ruta_consolidado, "w", encoding="utf-8") as archivo_salida:

            # Recorremos todos los CSV descargados
            for ruta_archivo in lista_archivos:
                log.info(f"Procesando archivo: {os.path.basename(ruta_archivo)}")
                # Abrimos cada archivo CSV individual
                with open(ruta_archivo, "r", encoding="utf-8") as archivo_entrada:
                    # Leemos todas las líneas
                    lineas = archivo_entrada.readlines()
                    # Si el archivo está vacío lo ignoramos
                    if not lineas:
                        continue
                    # Guardamos el encabezado SOLO del primer archivo
                    if not encabezado_guardado:
                        archivo_salida.write(lineas[0])
                        encabezado_guardado = True
                    # Agregamos todas las filas excepto el encabezado
                    archivo_salida.writelines(lineas[1:])
        log.info("Archivo consolidado correctamente")

        # Eliminamos archivos individuales
        for ruta_archivo in lista_archivos:
            os.remove(ruta_archivo)
            log.info(f"Archivo eliminado: {os.path.basename(ruta_archivo)}")
        # Retornamos la ruta final
        return ruta_consolidado, None

    except Exception as e:
        mensaje_error = f"Error al unificar archivos CSV: {e}"
        log.error(mensaje_error)
        return None, mensaje_error