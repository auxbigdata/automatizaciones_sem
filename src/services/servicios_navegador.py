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
            log.info("Abriendo Navegador con perfil")
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=perfil,
                headless=True,
                accept_downloads=True,
                downloads_path=ruta_descargas,
                channel="chrome"  # Usa Chrome real, no Chromium
            )
            page = context.pages[0] if context.pages else context.new_page()
        else:
            log.info("Abriendo Navegador")
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                accept_downloads=True,
            )
            page = context.new_page()
        
        if page:
            mensaje = "Navegador abierto exitosamente."
            return page, mensaje
    except Exception as e:
        error_msg = f"Error al abrir el navegador: {str(e)}"
        return None, error_msg


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
        
        return True, f"Login exitoso en {nombre_sitio}"
    except Exception as e:
        return False, f"Error al iniciar sesión en {nombre_sitio}: {e}"

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
    
    
#Funcion seleccionar fecha Cofrem 
def fecha_ayer(page, log, sel_inicio="input[name='fecini']", sel_fin="input[name='fecfin']"):
    try:
        ayer = datetime.now() - timedelta(days=1)
        fecha = ayer.strftime("%Y/%m/%d")

        log.info(f"Obteniendo fecha {fecha}")

        page.evaluate(f"""
            const ini = document.querySelector("{sel_inicio}");
            const fin = document.querySelector("{sel_fin}");

            if (!ini || !fin) {{
                throw new Error("No se encontraron los campos de fecha");
            }}

            ini.value = "{fecha}";
            fin.value = "{fecha}";

            ini.dispatchEvent(new Event('change', {{ bubbles: true }}));
            fin.dispatchEvent(new Event('change', {{ bubbles: true }}));
        """)

        return True

    except Exception as e:
        log.error(f"Error seteando fechas: {e}")
        return False

# Funcion descargar archivo Cofrem
def descargar_archivo_cofrem(page, log, selector_boton: str, timeout: int = 60000):
    try:
        log.info("Iniciando Descarga del archivo")
        page.wait_for_selector(selector_boton, timeout=30000)
        with page.expect_download(timeout=timeout) as download_info:
            page.click(selector_boton)
            
        download = download_info.value
        log.info("Descarga inciada correctamente")
        log.info(download)
        return download
    except Exception as e:
        log.error(f"error en la descarga {e}")
        return None

 