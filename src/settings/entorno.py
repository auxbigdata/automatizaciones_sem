# Archivo autogenerado por sync_env.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Entorno(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    
    ENV: str
    URL_SGC: str
    USER_COFREM: int
    PASS_COFREM: str
    URL_LOGIN_COFREM: str
    URL_HOME_COFREM: str
    URL_REPORTE_COFREM: str
    URL_SGC_SUBIR_ARCHIVO_COFRES: str
    URL_GRILLA: str
    URL_FINALIZAR_EMSA: str
    URL_DESCARTAR_EMSA: str
    URL_HOME_EMSA: str
    URL_DESCARGAR_PDF_EMSA: str
    URL_COMPARTIDA: str
    IP_COMPARTIDA: str
    USER_COMPARTIDA: str
    PASS_COMPARTIDA: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

# Instancia global lista para ser importada
env = Entorno()
