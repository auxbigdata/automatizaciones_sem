from playwright.sync_api import sync_playwright
 
url = "http://186.117.156.122:8082/Bonos/login.jsp"

with sync_playwright() as p:
    browser = p.firefox.launch()
    page = browser.new_page(headless=False)
    page.goto(url)
    browser.close()

# funcion para taerme el html de la pagina y respuesta si tenemos acceso a la pagina

import requests
def pagina_accesible(url):
    try:
        response = requests.get(
            url,
            timeout=5,
        )

        print("\n===== HTML RECIBIDO =====\n")
        print(response.text)   # 👈 IMPRIME EL HTML
        print("\n===== FIN HTML =====\n")

        if response.status_code == 200:
            return True
        else:
            return False

    except requests.exceptions.RequestException as e:
        print("❌ Error al acceder a la página")
        print(e)
        return False




if pagina_accesible(url):
    print("✅ ACCESO CONFIRMADO")
else:
    print("❌ SIN ACCESO")