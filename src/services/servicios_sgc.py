from datetime import datetime
import json
import os
import requests

def subir_facturacion(id_tercero: str, ruta_archivo: str, nombre_archivo: str, URL_UPLOAD, log: object):
    data = {
        "usuario": "CP1029980182",
        "tiemposesion": "1763499600887",
        "estadotiempo": "0",
        "comodin": "1",
        "como": "0",
        "tercero": f"{id_tercero}",
        "tipore2": "1",
        "tipore3": "1",
        "tipore26": "1",
        "tipore4": "1",
        "tipore": "0",
        "cantidad_1": "0",
        "submitBtn": "Subir"
    }
    # log.info("en la funcion subir_facturacion")
    # log.info("estructura de la data:")
    # log.info(data)
    session = requests.Session()

    # adjunta archivo a la peticion
    with open(ruta_archivo, "rb") as f:
        files = {
            "myfile": (nombre_archivo, f, "text/plain")
        }

        req = requests.Request(
            "POST",
            URL_UPLOAD,
            data=data,
            files=files
        )

        prepared = session.prepare_request(req)

        log.info("===== PETICIÓN ANTES DE ENVIAR =====")
        log.info(f"URL: {prepared.url}")
        log.info(f"MÉTODO: {prepared.method}")
        log.info(f"NOMBRE ARCHIVO: {nombre_archivo}")
        log.info("HEADERS:")
        log.info(prepared.headers)
        log.info("BODY:")
        # log.info(prepared.body)
        log.info("===================================")

        response = session.send(prepared)
            # response = session.post(URL_UPLOAD, data=data, files=files)
        # log.info(f"STATUS: {response.status_code}")
        # log.info("RESPUESTA:")
        # log.info(response.text)
        return response
    
def subir_archivo_cofres_inteligentes(ruta_archivo, log, URL):
    if not os.path.exists(ruta_archivo):
        log.error("El archivo no existe.")
        return None

    headers = {"Authentication": json.dumps({"nickname": 1029980182, "nivel": "1"})}
    data = {
        "json": json.dumps([{
            "con": "33",
            "usuario": 1029980182,
            "ip_address": "10.8.0.27",
            "fechasys": datetime.now().strftime("%Y-%m-%d"),
            "tipoa": "0",
            "tipo": "0"
        }]),
        "tipoa": "0"
    }

    log.info(f"Subiendo archivo: {os.path.basename(ruta_archivo)}")
    try:
        with open(ruta_archivo, "rb") as f:
            files = {"myfile": (os.path.basename(ruta_archivo), f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            r = requests.post(URL, headers=headers, data=data, files=files, timeout=120)
        log.info(f"Status: {r.status_code} | Respuesta: {r.text}")
        return r  # ← retornar response completo
    except Exception as e:
        log.error(f"Error subiendo archivo: {e}")
        return None
    