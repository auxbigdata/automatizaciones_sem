import base64
from datetime import datetime
import requests
import cgi
import os
import pandas as pd
import urllib
from src.services.utils import obtener_fecha_ayer, conectar_a_carpeta_compartida
import xml.etree.ElementTree as ET
import pdfplumber
import re
import urllib3
import smbclient
import zipfile
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def iniciar_sesion(url: str, headers: dict, payload: dict, log: object):
    try:
        log.info("Se inicia la peticion para inciar sesion")
        session = requests.Session()

        response = session.post(url, data=payload, headers=headers, timeout=60)
        
        # Verificamos si la petición fue exitosa (Status Code 200)
        log.info(response)
        log.info(f"Reason        : {response.reason}")
        log.info(f"URL final     : {response.url}")
        log.info(f"Encoding      : {response.encoding}")
        log.info(f"Headers       : {dict(response.headers)}")
        log.info(f"Cookies       : {dict(response.cookies)}")
        log.info(f"Request URL   : {response.request.url}")
        log.info(f"Request Method: {response.request.method}")
        log.info(f"Request Header: {dict(response.request.headers)}")

        if response.status_code == 200:
            log.info("Petición enviada exitosamente.")
            log.info(f"Respuesta del servidor: {response}")
            return session, response
        else:
            return False, response
    except requests.exceptions.Timeout:
        return False, "El servidor tardó demasiado en responder (Timeout)."
    except requests.exceptions.ConnectionError:
        return False, "No hubo conexión a internet o el DNS falló."
    except requests.exceptions.RequestException as e:
        return False, f"Ocurrió un error inesperado: {e}"

def descargar_reporte(session: object, url: str, headers: dict, payload: dict, log: object, ruta_descarga: str):
    try:
        if not os.path.exists(ruta_descarga):
            os.makedirs(ruta_descarga)
            log.info(f"Carpeta creada: {ruta_descarga}")

        # Usamos la sesión para pedir el archivo
        response = session.post(url, data=payload, stream=True, timeout=30)
            # r.raise_for_status() # Lanza error si el status no es 200
        
        content_disposition = response.headers.get('Content-Disposition')

        # if content_disposition:
        #     value, params = cgi.parse_header(content_disposition)
        #     nombre_archivo = params.get('filename', 'pagos_cofrem.txt')
        # else:
        #     log.info("El servidor no envió un nombre específico. Usando genérico.")
        #     nombre_archivo = "pagos_cofrem.txt"
        #     return None, f"No se encontró el archivo en la petición {content_disposition}", None

        # VALIDACIÓN CRÝTICA: Si no hay header o está vacío, abortamos
        if not content_disposition:
            log.error("El servidor no envió el encabezado Content-Disposition.")
            log.info(f"Codigo de estado: {response.status_code}")
            return None, f"No se encontró el archivo en la petición: Header ausente <br><br>Codigo de estado: {response.status_code} <br>URL: {url} <br>Parametros: {payload}", None

        # Si existe el header, extraemos el nombre
        value, params = cgi.parse_header(content_disposition)
        nombre_archivo = params.get('filename')

        # Si el header existe pero no contiene un 'filename'
        if not nombre_archivo:
            log.error(f"Header presente pero sin nombre de archivo: {content_disposition}")
            log.info(f"Codigo de estado: {response.status_code}")
            return None, f"No se pudo extraer el nombre del archivo de: {content_disposition} <br><br>Codigo de estado: {response.status_code} <br>URL: {url} <br>Parametros: {payload}", None

        ruta_completa = os.path.join(ruta_descarga, nombre_archivo)
        with open(ruta_completa, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        if os.path.exists(ruta_completa):
            return ruta_completa, f"Archivo descargado con su nombre original: {nombre_archivo}", nombre_archivo
        else:
            return None, f"Ocurrió un error al descargar el archivo en la ruta {ruta_completa}", None

    except requests.exceptions.RequestException as e:
        return None, f"Ocurrió un error en el proceso de descargar el archivo: {e}", None
    
def iniciar_sesion_brinks(log):
    session = requests.Session()

    url = "https://www.24sevenbrinks.com/api/v1/account/login"

    payload = {
        'password': 'C0nsu2025#',
        'username': 'rdiaz@consuerte.com.co'
    }
    # Cabeceras de navegador real
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es",
        "Sec-Ch-Ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        "Origin": "https://www.24sevenbrinks.com"
    }

    try:
        response = session.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            user_id = response.json().get("sub")

            # 1. Obtener ANTIFORGERY Y Token
            session.get("https://www.24sevenbrinks.com/api/v1/account/getantiforgerytoken")
            token_raw = session.cookies.get('CWP-SITE-XSRF-TOKEN') or ""
            session.headers.update({"X-XSRF-TOKEN": urllib.parse.unquote(token_raw)})

            # 2. Cargar Permisos y preferencias del usuario
            session.get(f"https://www.24sevenbrinks.com/api/v1/gateway/account-grants/grants/{user_id}")
            session.get(f"https://www.24sevenbrinks.com/api/v1/gateway/userpreferences/{user_id}")
            session.get("https://www.24sevenbrinks.com/api/v1/gateway/user")

            session.user_id = user_id
            log.info("Petición enviada exitosamente.")
            log.info(f"Respuesta del servidor: {response.json()}")
            return session, response
        else:
            log.info(f"Error en la Petición. Codigo de estado: {response.status_code}")
            return False, f"Login fallido. Código de estado: {response.status_code}"
    except Exception as e:
        log.info(f"Ocurrió un error de conexión: {e}")
        return False, f"Error de conexión: <br><br>{e}"

def descargar_reporte_brinks(session, ruta_descargas, log):
    url = "https://www.24sevenbrinks.com/api/v1/gateway/static-report/deposits-statement-report"

    # llamar funcion de utils
    ayer_str = obtener_fecha_ayer()
    ayer_dt = datetime.now()
    
    log.info(f"fecha para descargar el reporte: {ayer_str}")
    payload = {
        "renderType": 2,
        "initialDate": f"{ayer_str}T05:00:00.000Z",
        "endDate": f"{ayer_str}T05:00:00.000Z",
        "branchId": None,
        "contractCode": None,
        "countryId": None,
        "customerName": "CONSUERTE",
        "depositType": None,
        "endTime": None,
        "financialModality": None,
        "initialTime": None,
        "transporterId": None
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "Referer": "https://www.24sevenbrinks.com/es/static-report/deposits-statement-report",
        "Origin": "https://www.24sevenbrinks.com"
    }

    try:
        response = session.post(url, json=payload, headers=headers, stream = True, timeout=90)

        if response.status_code == 200:
            data_jason = response.json()
            contenido_base64 = data_jason.get("content")
            if not contenido_base64:
                log.info("El servidor respondio pero el campo 'content' está vacio.")
                return None
            archivo_bytes = base64.b64decode(contenido_base64)

            os.makedirs(ruta_descargas, exist_ok=True)
            nombre_archivo = f"Informe de Extracto de Depósitos_{ayer_dt.day}_{ayer_dt.month}_{str(ayer_dt.year)[2:]} {datetime.now().strftime('%H_%M')}.xlsx"
            ruta_final = os.path.join(ruta_descargas, nombre_archivo)

            with open(ruta_final, "wb") as f:
                f.write(archivo_bytes)
            log.info(f"Reporte guardado en: {ruta_final}")
            return ruta_final, "Reporte descargado exitosamente.", os.path.basename(ruta_final)  
        else:
            log.error(f"Error {response.status_code}: {response.text}")
            return None, f"Error al descargar el reporte. Código: {response.status_code}", None  
    except requests.exceptions.RequestException as e:
        log.info(f"Ocurrió un error de conexión: {e}")
        return None, f"Error de conexión: {e}", None     
    
# -------------------------------ROBOT SERVICIOS PUBLICOS----------------------------------------------
def verificar_url_emsa(url:str, log:object):
    try:
        log.info(f"verificando disponibilidad de URL{url}")
        response = requests.get(url, timeout=15, verify=False)
        
        if response.status_code == 200:
            log.info(f"URL disponible - Código: {response.status_code}")
            return True, "OK"
        else:
           log.info(f"URL responde pero con código inesperado: {response.status_code}")
        return False, f"URL responde pero con código inesperado: {response.status_code}"

    except requests.exceptions.Timeout:
        log.error("El servidor no respondio a tiempo (Timeout).")
        return False, "El servidor no respondio a tiempo (Timeout)."
    except requests.exceptions.ConnectionError:
        log.error("No se pudo conectar al servidor.")
        return False, "No se pudo conectar al servidor."
    except requests.exceptions.RequestException as e:
        log.error(f"Error inesperado al verificar URL: {e}")
        return False, f"Error inesperado al verificar URL: {e}"

def consultar_grilla_emsa(url: str, headers: dict, log: object):
    try:
    # Realizamos la petición POST
        response = requests.post(url, headers=headers, timeout=30)
        
        # Verificamos si la petición fue exitosa (Status Code 200)
        if response.status_code == 200:
            log.info("Petición enviada exitosamente.")
            # log.info("Respuesta del servidor:", response.text)
            codigos_cliente = response.text
            return codigos_cliente
        else:
            log.info(f"Error en la petición. Código de estado: {response.status_code}")

    except requests.exceptions.RequestException as e:
        log.info(f"Ocurrió un error de conexión: {e}")

def validar_contenido_factura(url, log: object):

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    log.info(f"Se procede a validar el tipo de contenido de url: {url}")
    try:
        response = requests.get(url, timeout=30, verify=False)
        #status_code = response.status_code
        content_type = response.headers.get("Content-Type")
        #txt_response = response.text
        return content_type
    except requests.exceptions.RequestException:
        status_code = None

def descarga_facturas_emsa(url):

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        response = requests.get(url, timeout=30, verify=False)
        #status_code = response.status_code
        content_type = response.headers.get("Content-Type")
        #txt_response = response.text
        return content_type
    except requests.exceptions.RequestException:
        status_code = None


def descartar_emsa(url: str, log: object, headers: dict, codigo:str, punto_venta:str, novedad:str):
    try:# Realizamos la petición POST
        payload = {
            "codigo": codigo,
            "puntoVenta":punto_venta,
            "novedad": novedad
        }
        log.info(f"descartando  factura{codigo}- {punto_venta} | novedad: {novedad}")

        # Cambiamos data=payload por json=payload
        # el servidor recibe JSON correctamente, que es lo que espera el endpoint
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            log.info(f"Factura {codigo} descartada correctamente.")
            log.info(f"Respuesta del servidor : {response.text}")
            return response.text #retornamos para saber si la respuesta fue exitosa
        else:
            log.error(f"Error al descartar. codigo: {response.status_code}| respuesta: {response.text}")
            return None #retornamos none para indicar que fallo
        
    except requests.exceptions.RequestException as e:
        log.info(f"Ocurrió un error de conexión: {e}")
        return None
    
def finalizar_emsa(url: str, log: object, headers: dict, codigo: str, punto: str, fecha: str, valor: str, novedad: str):
    try:# Realizamos la petición POST
        payload = {
            "codigo": codigo,
            "punto":punto,
            "fecha":fecha,
            "valor":valor,
            "novedad": novedad
        }
        log.info(f"finalizando factura{codigo} -  - {punto} | valor: {valor} | fecha: {fecha}")

        # Cambiamos data=payload por json=payload
        # el servidor recibe JSON correctamente, que es lo que espera el endpoint
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            log.info(f"Factura {codigo} Finalizado correctamente.")
            log.info(f"Respuesta del servidor : {response.text}")
            return response.text #retornamos para saber si la respuesta fue exitosa
        else:
            log.error(f"Error al descartar. codigo: {response.status_code}| respuesta: {response.text}")
            return None #retornamos none para indicar que fallo
        
    except requests.exceptions.RequestException as e:
        log.info(f"Ocurrió un error de conexión: {e}")

# -----------------------------DESCARGA PDF RECIBO EMSA SERVICIOS PUBLICOS------------------------------------------------
def descargar_pdf(url: str, nombre_pdf: str, ruta_descarga: str, log: object):
    try:
        log.info(f"iniciando descarga pdf del cliente {url}")

        # if not os.path.exists(ruta_descarga):
        #     os.makedirs(ruta_descarga)

        response = requests.get(url, timeout=30, verify=False)

        log.info(f"codigo de estado :{response.status_code}")
        log.info(f"URL consultada : {url}")
        log.info(f"Content-Type: {response.headers.get('Content-Type')}")

        if response.status_code != 200:
            log.error(f"Error en la respuesta del servidor: {response.status_code}") 
            return None, f"Error HTTP: {response.status_code}", False
        
        # verificamos que realmente sea un pdf
        content_type = response.headers.get("Content-Type", "")
        if "application/pdf" not in content_type:
            log.error(f"El servidor respondió 200 pero el contenido no es PDF. Content-Type recibido: {content_type}")
            return None, f"Contenido no es PDF. Content-Type: {content_type}", False

        #AQUÍ ESTÁ LA CLAVE
        pdf_bytes = response.content

        # ruta_pdf = os.path.join(ruta_descarga, f"{nombre_pdf}.pdf")
        ruta_pdf = rf"{ruta_descarga}\{nombre_pdf}.pdf"

        try:
            with smbclient.open_file(ruta_pdf, mode='wb') as f:
                f.write(pdf_bytes)
        # with open(ruta_pdf, "wb") as f:
        #     f.write(pdf_bytes)
        except Exception as e:
            log.error(f"Error al escribir el archivo: {e}")
            return None, f"Error al escribir el archivo: {e}", False

        if smbclient.path.isfile(ruta_pdf):
            log.info(f"PDF descargado correctamente: {ruta_pdf}")
            return ruta_pdf, f"PDF descargado correctamente: {ruta_pdf}", True
        else:
            log.error(f"El archivo no se encontró en la ruta tras la escritura: {ruta_pdf}")
            return None, f"Error: No se pudo verificar la existencia del archivo en {ruta_pdf}", False

    except Exception as e:
        log.error(f"Error inesperado: {e}")
        return None, f"Error inesperado: {e}", False

def generar_excel_consolidado(datos:list, ruta_descarga:str,nombre_archivo:str,log:object):
    try:

        # obtenemos fecha
        fecha_hoy=datetime.now().strftime("%Y-%m-%d")

        ruta_consolidado=os.path.join(ruta_descarga,fecha_hoy)

        # si la carpeta no exite se crea
        if not os.path.exists(ruta_consolidado):
            os.mkdir(ruta_consolidado)
            log.info(f"carpeta creada exitosamente:{ruta_consolidado}")
        
        ruta_excel = os.path.join(ruta_consolidado,nombre_archivo)

        # creamos el dataframe
        df=pd.DataFrame(datos)

        # convertimos valor_pago a numerico para que en excel no quede como texto
        if "valor_pago" in df.columns:
            df["valor_pago"] = pd.to_numeric(df["valor_pago"], errors="coerce")

        # exportamos a excel
        with pd.ExcelWriter(ruta_excel, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Consolidado")

            hoja = writer.sheets["Consolidado"]

            # estilos de encabezado
            fuente_encabezado = Font(bold=True, color="FFFFFF")
            relleno_encabezado = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            alineacion_centro = Alignment(horizontal="center", vertical="center")
            borde_fino = Border(
                left=Side(style="thin", color="B7B7B7"),
                right=Side(style="thin", color="B7B7B7"),
                top=Side(style="thin", color="B7B7B7"),
                bottom=Side(style="thin", color="B7B7B7"),
            )

            columna_valor_pago = None
            for idx, nombre_columna in enumerate(df.columns, start=1):
                if nombre_columna == "valor_pago":
                    columna_valor_pago = idx

                celda_encabezado = hoja.cell(row=1, column=idx)
                celda_encabezado.font = fuente_encabezado
                celda_encabezado.fill = relleno_encabezado
                celda_encabezado.alignment = alineacion_centro
                celda_encabezado.border = borde_fino

            # formato de las filas de datos y ancho de columnas
            for idx, nombre_columna in enumerate(df.columns, start=1):
                letra_columna = get_column_letter(idx)
                ancho_maximo = max(
                    [len(str(nombre_columna))] + [len(str(valor)) for valor in df[nombre_columna]]
                )
                hoja.column_dimensions[letra_columna].width = ancho_maximo + 4

                for fila in range(2, len(df) + 2):
                    celda = hoja.cell(row=fila, column=idx)
                    celda.border = borde_fino
                    celda.alignment = Alignment(horizontal="center", vertical="center")
                    if idx == columna_valor_pago:
                        celda.number_format = '"$" #,##0'

        # validamos que el archivo existe
        if os.path.exists(ruta_excel):
            log.info(f"Excel generado correctamente")
            return ruta_excel

        return None
    except Exception as e:
        log.error(f"Error generando Excel: {e}")
        return None
    
    # generamos archvio zip con los consolidados de los puntos procesados
# def generar_zip_consolidado(archivos_procesados:str,archivos_no_procesados:str, log:object):
#     try:
#         log.info("iniciando generacion de archivo zip consolidado")

#         # validamos los parametros recibidos
#         if not archivos_procesados:
#             return None,"No se recibio la ruta del archivo procesado",False

#         if not archivos_no_procesados:
#             return None,"No se recibio la ruta del archivo procesado",False
        
#         # validar exitencia de los archivos excel
#         if not os.path.exists(archivos_procesados):
#             return None, f"No existe el archivo {archivos_procesados}", False

#         if not os.path.exists(archivos_no_procesados):
#             return None, f"No existe el archivo {archivos_no_procesados}", False

#         # obtenemos carpeta destino
#         carpeta_destino= os.path.dirname(archivos_procesados)
#         if not os.path.exists(carpeta_destino):
#             return None, f"La carpeta no existe {carpeta_destino}", False
        
#         # nombre del archvio zip
#         fecha_actual=datetime.now().strftime("%Y%m%d")

#         nombre_zip = (
#             f"consolidado_puntos_servicios_publicos{fecha_actual}.zip"
#         )

#         ruta_zip = os.path.join(
#             carpeta_destino,
#             nombre_zip
#         )

#         # creamos zip
#         with zipfile.ZipFile(
#             ruta_zip,
#             mode="w",
#             compression=zipfile.ZIP_DEFLATED
#         ) as zipf:
#             log.info(f"agregando archivo  procesados")
#             zipf.write(archivos_procesados,arcname=os.path.basename(archivos_procesados))

#             log.info(f"agregando archivo no procesados")
#             zipf.write(archivos_no_procesados,arcname=os.path.basename(archivos_no_procesados))

#         # validamos creacion del zip
#         if not os.path.exists(ruta_zip):
#             return (
#                 None,
#                 f"No se pudo generar el ZIP {ruta_zip}",
#                 False
#             )
        
#         log.info("generando archivo zip")
#         return ruta_zip,"ZIP generado correctamente", True
#     except Exception as e:
#         mensaje = (
#             f"Error al generar el ZIP. "
#             f"Detalle: {str(e)}")
#         log.exception(mensaje)
#         return None, mensaje, False

