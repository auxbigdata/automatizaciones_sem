from dotenv import load_dotenv
from dataclasses import dataclass
import os

@dataclass
class Entorno:
    URL_SGC: str
    ENV: str
    USER_COFREM: str
    PASS_COFREM: str
    URL_LOGIN_COFREM: str
    URL_HOME_COFREM: str
    URL_REPORTE_COFREM: str
    URL_SGC_SUBIR_ARCHIVO_COFRES: str

load_dotenv()

env = Entorno(
    URL_SGC=os.getenv("URL_SGC"),
    ENV=os.getenv("ENV"),
    USER_COFREM=os.getenv("USER_COFREM"),
    PASS_COFREM=os.getenv("PASS_COFREM"),
    URL_LOGIN_COFREM=os.getenv("URL_LOGIN_COFREM"),
    URL_HOME_COFREM=os.getenv("URL_HOME_COFREM"),
    URL_REPORTE_COFREM=os.getenv("URL_REPORTE_COFREM"),
    URL_SGC_SUBIR_ARCHIVO_COFRES=os.getenv("URL_SGC_SUBIR_ARCHIVO_COFRES")
    )

print(env.URL_SGC)
print(env.ENV)