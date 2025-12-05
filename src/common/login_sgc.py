from .browser import open_browser


def iniciar_sesion_sgc(page, URL, URL_HOME, PASS, USER):
    # logging.info("Se procede a iniciar sesion")
    try:
        #PRODUCCION
        page.goto(f"{URL}/index.php")

        #USUARIO 
        input_usuario = page.wait_for_selector('input#usuario_real',state='visible')
        input_usuario.fill(USER)

        #CONTRASEÑA
        # page.wait_for_selector('#float-input-password',state='visible')
        # page.fill('#float-input-password', PASS)
        input_pass = page.wait_for_selector('input#password_real',state='visible')
        input_pass.fill(PASS)

        page.wait_for_timeout(10000)  # Esperar 1 segundo para que los campos se llenen

        page.locator("#btningresar").click()
        # page.get_by_text("Entrar").click()

        page.wait_for_url(URL_HOME, timeout=25000)  # Ajusta 
        # logging.info("Se incia sesion correctamente")
        print("Login exitoso")
    except Exception as e:
        # logging.error(f"Ocurrio un error al iniciar sesión es superflex: {e}")
        print(f"Ocurrio un error al iniciar sesión en sgc: {e}")