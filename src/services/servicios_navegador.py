from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

# def abrir_navegador_con_perfil(perfil: str):
#     # perfil_chrome = r"C:\\Users\\userapp\\AppData\\Local\\Google\\Chrome\\User Data\\Consuerte\\WhatsApp"

#     p = sync_playwright().start()

#     context = p.chromium.launch_persistent_context(
#         user_data_dir=perfil,
#         channel='chrome',
#         headless=False,
#     )

#     page = context.new_page()
#     return page




def abrir_navegador(ruta_descargas: str, log: object, perfil: str = None):
    try:    
        playwright = sync_playwright().start()
        
        if perfil:
            log.info("Abriendo Navegador")
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=perfil,
                headless=True,
                accept_downloads=True,
                downloads_path=ruta_descargas,
                channel="chrome"  # Usa Chrome real, no Chromium
            )
            page = context.pages[0] if context.pages else context.new_page()
            browser = None
        else:
            log.info("Abriendo Navegador")
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                accept_downloads=True,
            )
            page = context.new_page()
        return page
    except Exception as e:
        return None


def login(page, config):
    """
    Función genérica para iniciar sesión en cualquier plataforma.
    :param page: Objeto 'page' de Playwright.
    :param config: Diccionario con selectores, credenciales y URLs.
        ej:
        config_superflex = 
        {
            "nombre": "Superflex",
            "url_login": "https://url-de-superflex.com",
            "url_home": "https://url-del-home.com",
            "user": USER,
            "password": PASS,
            "sel_user": "#float-input",
            "sel_pass": "#float-input-password",
            "sel_button": "#float-input-password",
            "btn_text": "Ingresar" # Buscamos por el texto del botón
        }
    :param log: Objeto logger para trazabilidad.
    """
    try:
        nombre_sitio = config.get("nombre", "Sitio Desconocido")
        # 1. Navegación
        page.goto(config["url_login"])
        page.wait_for_timeout(5000)  # Esperar 10 segundos para que la página cargue completamente
        
        # 2. Llenado de Usuario
        page.wait_for_selector(config["sel_user"], state='visible', timeout=15000)
        page.fill(config["sel_user"], config["user"])
        
        # 3. Llenado de Contraseña
        page.wait_for_selector(config["sel_pass"], state='visible', timeout=15000)
        page.fill(config["sel_pass"], config["password"])
        
        # 4. Click en el botón de ingreso
        # Soporta tanto selectores CSS como búsqueda por texto
        if config.get("btn_selector"):
            page.click(config["btn_selector"])
        elif config.get("sel_button"):
            page.click(config["sel_button"])
        elif config["sel_button"]:
            page.get_by_text(config["sel_button"]).click()
        else:
            page.keyboard.press("Enter")

        # 5. Verificación de éxito
        # Espera a que la URL cambie a la de Home o que aparezca un elemento del dashboard
        page.wait_for_url(config["url_home"], timeout=30000)
        
        print(f"✅ Login exitoso en {nombre_sitio}")
        return True

    except Exception as e:
        print(f"❌ Error al iniciar sesión en {nombre_sitio}: {e}")
        return False

def ir_a_url(page, url: str, log):
    try:
        log.info(f"Navegando a {url}")
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle")
        log.info("Navegacion Exitosa")
        return True
    except Exception as e:
        log.error(f"Error Navegando a{url}: {e}")
        return False


# Funcion Obtener Fecha Cofrem
def obtener_fecha_ayer(formato: str = "%Y/%m/%d"):
    ayer = datetime.now() - timedelta(days=1)
    fecha_ayer = 
    
# USER = "800159687"
# PASS = "C0ns43rt3"

# config = {
#     "nombre": "cofrem",
#     "url_login": "http://186.117.156.122:8082/Bonos/login.jsp",
#     "url_home": "http://186.117.156.122:8082/Bonos/request-manager.jsp",
#     "user": USER,
#     "password": PASS,
#     "sel_user": "input[name='id_usuario']",
#     "sel_pass": "input[name='pwd_usuario']",
#     "sel_button": "button[type='submit']"
#     # "btn_text": "" # Buscamos por el texto del botón
# }

 