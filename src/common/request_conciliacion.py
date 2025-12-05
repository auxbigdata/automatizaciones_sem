# import requests
import requests

def request_conciliacion(data, ruta_archivo: str, nombre_archivo: str, URL_UPLOAD):

    data = {
        "usuario": "CP1029980182",
        "tiemposesion": "1763499600887",
        "estadotiempo": "0",
        "comodin": "1",
        "como": "0",
        "tercero": "495",
        "tipore2": "1",
        "tipore3": "1",
        "tipore26": "1",
        "tipore4": "1",
        "tipore": "0",
        "cantidad_1": "0",
        "submitBtn": "Subir"
    }
    # 4. Archivo a subir
    # ruta = "C:/automatizaciones_sem/src/robots/punto_red/archivos_punto_red/RCONL_090_251118.txt"
    print("en la funcion request_conciliacion")
    session = requests.Session()

    with open(ruta_archivo, "rb") as f:
        files = {
            "myfile": (nombre_archivo, f, "text/plain")
        }

        response = session.post(URL_UPLOAD, data=data, files=files)

    print("STATUS:", response.status_code)
    print("RESPUESTA:")
    print(response.text)
    return response
