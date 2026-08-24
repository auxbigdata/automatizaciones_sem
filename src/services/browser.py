from playwright.sync_api import sync_playwright
import subprocess
import time

def open_browser(headless=True, workspace=None, log=None):
    """
    :param workspace: si se indica (0 = primer espacio de trabajo, 1 = segundo, etc.),
        se intenta mover la ventana de Firefox a ese espacio de trabajo apenas se abre,
        para que no aparezca encima de lo que el usuario esté usando en su escritorio
        actual. Solo aplica con headless=False y requiere un gestor de ventanas real
        (no aplica en xvfb). Si falla, no interrumpe el proceso.
    """
    p = sync_playwright().start()
    browser = p.firefox.launch(headless=headless)
    page = browser.new_page()

    if not headless and workspace is not None:
        _mover_ventana_a_workspace(workspace, log=log)

    return page

def _mover_ventana_a_workspace(workspace, log=None, intentos=5, espera_segundos=1):
    # la ventana de Firefox puede tardar un instante en aparecer para el gestor de
    # ventanas, por eso se reintenta unas cuantas veces antes de rendirse
    for intento in range(1, intentos + 1):
        try:
            resultado = subprocess.run(
                ["xdotool", "search", "--onlyvisible", "--class", "firefox"],
                capture_output=True, text=True, timeout=10
            )
            ventanas = resultado.stdout.split()
            if ventanas:
                for ventana in ventanas:
                    subprocess.run(["xdotool", "set_desktop_for_window", ventana, str(workspace)], timeout=10)
                if log:
                    log.info(f"Ventana(s) de Firefox movida(s) al espacio de trabajo {workspace + 1}")
                return
        except Exception as e:
            if log:
                log.warning(f"No se pudo mover la ventana de Firefox al espacio de trabajo {workspace + 1}: {e}")
            return
        time.sleep(espera_segundos)

    if log:
        log.warning(f"No se encontró ninguna ventana de Firefox para mover al espacio de trabajo {workspace + 1}")
