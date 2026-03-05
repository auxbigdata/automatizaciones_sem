import requests
import cgi
import os

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

        # VALIDACIÓN CRÍTICA: Si no hay header o está vacío, abortamos
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

