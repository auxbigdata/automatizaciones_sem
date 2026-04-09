import base64
from datetime import datetime
import requests
import cgi
import os
import urllib
from src.services.utils import obtener_fecha_ayer
import xml.etree.ElementTree as ET

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
        return False, f"Error de conexión: {e}"

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

# def descargar_xml_emsa(url: str, codigo_cliente: str, ruta_descarga: str, log: object):
#     try:
#         log.info(f"descargando XML del cliente {codigo_cliente}")

#         if not os.path.exists(ruta_descarga):
#             os.makedirs(ruta_descarga)

#         response = requests.get(url, verify=False)

#        # Sacamos el nombre original del archivo desde la URL final
#         nombre_archivo = response.url.split('/')[-1].split('?')[0]
#         ruta_completa = os.path.join(ruta_descarga, nombre_archivo)

#         with open(ruta_completa, "wb") as f:
#             f.write(response.content)

#         # log.info(f"XML guardado como: {nombre_archivo}")
#         # log.info(f"XML guardado en  : {ruta_completa}")
#         return ruta_completa, None

#     except requests.exceptions.Timeout:
#         return None, f"Timeout al descargar XML del cliente {codigo_cliente}"
#     except requests.exceptions.ConnectionError:
#         return None, f"Error de conexión al descargar XML del cliente {codigo_cliente}"
#     except requests.exceptions.RequestException as e:
#         return None, f"Error inesperado: {e}"
    
# def leer_xml_emsa(ruta_xml: str, log: object):
#     try:
#         log.info(f"leyendo xml: {ruta_xml}")
        
#         estructura_xml = ET.parse(ruta_xml)
#         datos_xml = estructura_xml.getroot()

#         valor = ""
#         fecha = ""

#         ns = {
#             # busca etiquetas en el xml que tiene namespace(identificador unico para etiquetas)
#             'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
#         }

#         # el find() sirve para buscar un solo elemento
#         description = datos_xml.find('.//cbc:Description', ns)

#         if description is not None and description.text:
#             xml_interno = description.text.strip()

#             root_interno = ET.fromstring(xml_interno)
        
#         # el findall() busca muchos elementos
#         for note in root_interno.findall('.//cbc:Note', ns):
#             texto = note.text

#             if texto and 'DAT39_ASEO' in texto:
#                 valor = texto.split(":")[-1]

#             elif texto and 'FECH_VENC' in texto:
#                 fecha = texto.split(":")[-1]

#         return valor, fecha, None

#     except ET.ParseError as e:
#         log.error(f"El archivo no es un XML válido: {e}")
#         return None, None, f"XML inválido: {e}"

#     except Exception as e:
#         log.error(f"Error inesperado al leer XML: {e}")
#         return None, None, str(e)

# -----------------------------DESCARGA PDF RECIBO EMSA------------------------------------------------
