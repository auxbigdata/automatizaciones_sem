from dotenv import load_dotenv
from dataclasses import dataclass
import os

@dataclass
class Entorno:
    URL_SGC: str
    ENV: str

load_dotenv()

env = Entorno(
    URL_SGC=os.getenv("URL_SGC"),
    ENV=os.getenv("ENV")
    )

print(env.URL_SGC)
print(env.ENV)