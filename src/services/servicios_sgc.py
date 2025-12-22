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
        log.info("HEADERS:")
        log.info(prepared.headers)
        log.info("BODY:")
        log.info(prepared.body)
        log.info("===================================")

        response = session.send(prepared)
            # response = session.post(URL_UPLOAD, data=data, files=files)
        # log.info(f"STATUS: {response.status_code}")
        # log.info("RESPUESTA:")
        # log.info(response.text)
        return response