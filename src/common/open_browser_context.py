from playwright.sync_api import sync_playwright

def open_browser_context(perfil_chrome):
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=perfil_chrome,
            channel='chrome',
            headless=False,
            # args=[
            #     "--profile-directory=WhatsApp"   # nombre del perfil dentro de la carpeta
            # ]
        )

        return context

    
