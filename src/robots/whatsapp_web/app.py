from src.common.whatsapp_web import abrir_whatsapp_con_perfil, cerrar_navegador
from src.common.whatsapp_web import buscar_chats, ingresar_menu_comunidades, click_chat, enviar_imagen
from src.robots.whatsapp_web.validar_imagen import buscar_imagen
from src.common.open_browser_context import open_browser_context

# nombre_grupo = "RESULTADOS COLOMBIA"
# # "Resultados ConSuerte Acac",
grupos = [
        "Resultados ConSuerte Bet2",
        "Resultados ConSuerte BetP",
        "Resultados ConSuerte Mese",
        "Resultados ConSuerte PLop",
        "Resultados ConSuerte Z1",
        "Resultados ConSuerte Z2",
        "Resultados ConSuerte Z3",
        "Resultados ConSuerte Z4",
        "Resultados ConSuerte ZAr2",
        "Resultados ConSuerte ZAri",
        "Resultados ConSuerte ZCan",
        "Resultados ConSuerte ZCum",
        "Resultados ConSuerte Acac"
    ]
# # nombre_grupo = "Jairo Patino"

# page = abrir_whatsapp_con_perfil()
# ingresar_menu_comunidades(page)


ruta_imagen = buscar_imagen()
if ruta_imagen is not None:
    page = abrir_whatsapp_con_perfil()
    
    input("ESPERANDO QUE CARGUE WsHATSAPP...")

    ingresar_menu_comunidades(page)

    for grupo in grupos:
        # input("antes de iterar grupos")
        click_chat(page, grupo)
        enviar_imagen(page, ruta_imagen)
        page.wait_for_timeout(10000)
        # input(f"Presiona Enter para ir al siguiente grupo: {grupo}...")
    # buscar_chats(page, grupo)
    page.wait_for_timeout(10000)
    # input(f"Presiona Enter para ir al siguiente grupo: {grupo}...")
    cerrar_navegador(page)

    
# buscar_chats(page, nombre_grupo)
input("Presiona Enter para cerrar...")