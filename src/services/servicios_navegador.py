from playwright.sync_api import sync_playwright


def abrir_navegador_con_perfil(perfil: str):
    # perfil_chrome = r"C:\\Users\\userapp\\AppData\\Local\\Google\\Chrome\\User Data\\Consuerte\\WhatsApp"

    p = sync_playwright().start()

    context = p.chromium.launch_persistent_context(
        user_data_dir=perfil,
        channel='chrome',
        headless=False,
    )

    page = context.new_page()
    return page

def navegador_modo_headless():
    