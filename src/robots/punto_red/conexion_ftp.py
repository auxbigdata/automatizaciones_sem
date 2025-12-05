from ftplib import FTP
from ftplib import FTP
from datetime import datetime
import os
# ftp = FTP()
# ftp.connect('10.8.0.23', 2121)
# ftp.login(user='traeconsuerte', passwd='800159687')
# ftp.set_pasv(True)

# print("Conectado exitosamente")
# 
archivos = []


def conectar_ftp(host: str, puerto: int, user: str, passwd: str):
    """Establece y retorna una conexiÃƒÆ’Ã‚Â³n FTP lista para usar."""
    ftp = FTP()
    ftp.connect(host, puerto)
    ftp.login(user=user, passwd=passwd)
    ftp.set_pasv(True)
    print("Conectado exitosamente al FTP")
    return ftp

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
    print(dia_actual, mes_actual, anio_actual)
    print("Nombre del archivo a buscar:", nombre_archivo)
    # datetime.now().strftime('%y')
    return nombre_archivo


def descargar_archivo(ftp: FTP, nombre_archivo: str, ruta_descarga: str) -> bool:
    """Busca y descarga el archivo especificado. Retorna True si lo logra."""
    
    archivos = obtener_archivos_txt(ftp)
    ultimos_10 = archivos[-10:]

    os.makedirs(ruta_descarga, exist_ok=True)
    ruta_archivo = os.path.join(ruta_descarga, nombre_archivo)

    print("ÃƒÆ’Ã…Â¡ltimos 10 archivos:")
    for fecha, nombre in ultimos_10:
        print(f"{fecha} -> {nombre}")
        if nombre == nombre_archivo:
            print(f"Archivo encontrado: {nombre}")


            with open(ruta_archivo, 'wb') as f:
                ftp.retrbinary(f"RETR {nombre}", f.write)
            print(f"Archivo {nombre} descargado correctamente.")
            return True, ruta_archivo

    print("El archivo no se encontrÃƒÆ’Ã‚Â³ en los ÃƒÆ’Ã‚Âºltimos 10 registros.")
    return False, None


# ultimos_10 = archivos[-10:]

# print("ultimos 10 archivos .txt:")
# nombre_archivo = obtener_nombre_archivo()
# for fecha, nombre in ultimos_10:
#     print(f"{fecha} -> {nombre}")
#     if nombre == nombre_archivo:
#         print(f"ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ Archivo encontrado: {nombre}")
#         with open(nombre, 'wb') as f:
#             ftp.retrbinary(f'RETR {nombre}', f.write)
#             print(f"Archivo {nombre} descargado exitosamente.")
#         break

# ftp.quit()
# print("Se finaliza el proceso de descarga.")
