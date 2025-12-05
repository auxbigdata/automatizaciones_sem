from playwright.sync_api import sync_playwright
import time

def abrir_whatsapp_con_perfil():
    # perfil_chrome = r"C:\\Users\\userapp\\AppData\\Local\\Google\\Chrome\\User Data\\Consuerte\\WhatsApp"

    p = sync_playwright().start()
    # browser = p.firefox.launch(headless=headless)
    # page = browser.new_page()


    context = p.chromium.launch_persistent_context(
        user_data_dir=perfil_chrome,
        channel='chrome',
        headless=False,
        # args=[
        #     "--profile-directory=WhatsApp"   # nombre del perfil dentro de la carpeta
        # ]
    )

    page = context.new_page()
    page.goto("https://web.whatsapp.com")

    print("WhatsApp Web cargado con el perfil existente.")
    # input("Presiona Enter para cerrar...")

        # page.wait_for_timeout(15000)
    return page

def ingresar_menu_comunidades(page):
    page.locator("button[aria-label='Comunidades']").click()
    time.sleep(2)

    # page.locator().click()
    selector = "div[aria-label='Ver todos los subgrupos en Resultados Loteria']"
    # selector = "div[aria-label='Resultados Loteria']"
    page.locator(selector).wait_for(state="visible", timeout=8000)
    page.locator(selector).click()

def buscar_chats(page, nombre_grupo):

    items = page.locator("div[role='listitem'] span[title]").all()
    items = page.locator("div[role='listitem'] span[title]").all()
    print("=== TITULOS REALES ===")
    for i in items:
        title = i.get_attribute("title")
        print(repr(title))  # <--- muestra caracteres invisibles 



    selector = f"div[role='listitem'] span[title='{nombre_grupo}']"
    page.locator(selector).wait_for(state="visible", timeout=8000)
    page.locator(selector).click()

def click_chat(page, nombre):
    selector = f"span[title='{nombre}']"

    for _ in range(25):  # 25 scrolls hacia abajo
        elementos = page.locator(selector)

        # si hay coincidencias:
        count = elementos.count()

        if count >= 1:
            # elegir el PRIMER visible
            for item in elementos.all():
                if item.is_visible():
                    item.click()
                    print(f"Grupo abierto: {nombre}")
                    return True

        # si no lo encuentra aÃƒÂºn: hacer scroll
        page.mouse.wheel(0, 900)
        time.sleep(0.4)

    raise Exception(f"No se encontro el grupo: {nombre}")

def enviar_imagen(page, ruta_imagen):
    # 1. Cargar la imagen en el input invisible
    # Clic en el botÃƒÂ³n "+"
    page.locator("span[data-icon='plus-rounded']").click()

    page.set_input_files("input[accept*='image']", ruta_imagen)

    # 2. Esperar a que aparezca la vista previa
    # input("Se cargÃƒÂ³ la imagen, presiona Enter para continuar...")
    boton = page.locator("div[role='button'][aria-label='Enviar']")

    boton.click(timeout=5000)

    print("Ã¢Å“â€� Imagen enviada correctamente.")

def cerrar_navegador(page):
    try:
        context = page.context
        page.close()
        context.close()  # Esto cierra TODO el navegador con persistent context
        print("Ã¢Å“â€� Navegador cerrado correctamente")
    except Exception as e:
        print(f"Ã¢Å¡Â  Error cerrando navegador: {e}")