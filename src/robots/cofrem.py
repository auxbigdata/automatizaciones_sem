from src.services.servicios_navegador import login, abrir_navegador, ir_a_url
from src.settings.config import parametrizar_logs_y_ruta_archivos


robot = "cofrem"
log,ruta_descarga = parametrizar_logs_y_ruta_archivos(robot)

url2 = "http://186.117.156.122:8082/Bonos/request-manager.jsp?res=ges-downloadpaylistc"

USER = "800159687"
PASS = "C0ns43rt3"

config = {
    "nombre": "cofrem",
    "url_login": "http://186.117.156.122:8082/Bonos/login.jsp",
    "url_home": "http://186.117.156.122:8082/Bonos/request-manager.jsp",
    "user": USER,
    "password": PASS,
    "sel_user": "input[name='id_usuario']",
    "sel_pass": "input[name='pwd_usuario']",
    "sel_button": "button[type='submit']"
    # "btn_text": "" # Buscamos por el texto del botón
    }
page = abrir_navegador(
    log=log,
    ruta_descargas= ruta_descarga
)

if page is None:
    log.error("No se pudo abrir el navegador")
    raise Exception("Fallo al abir el Navegador")

login_exitoso = login(page, config)

if not login_exitoso:
    log.error("No se pudo inciar sesion en Cofrem")
    raise Exception("Login Fallido")

log.info("Login en cofrem realizado correctamente")

ok = ir_a_url(page,url2,log)
if not ok:
    raise Exception("No se pudo navegar a la URL 2")
