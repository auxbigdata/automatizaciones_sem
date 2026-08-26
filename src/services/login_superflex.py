from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import traceback
import re
import os
import subprocess
import time
from datetime import datetime

def asegurar_tray_icon_superflex(log=object):
    """
    Superflex necesita que superflex-tray-icon.jar esté corriendo para funcionar
    correctamente.
    """
    try:
        resultado = subprocess.run(
            ["pgrep", "-f", "superflex-tray-icon.jar"],
            capture_output=True, text=True
        )
        if resultado.returncode == 0:
            log.info(f"superflex-tray-icon.jar ya está corriendo (PID {resultado.stdout.split()[0]})")
            return True, "superflex-tray-icon.jar ya estaba corriendo"

        log.info("superflex-tray-icon.jar no está corriendo, se procede a iniciarlo")
        ruta_downloads = os.path.expanduser("~/Downloads")

        # se lanza en segundo plano y desligado de este proceso (start_new_session)
        # para que el tray icon quede corriendo aunque el robot termine
        subprocess.Popen(
            ["java", "-jar", "superflex-tray-icon.jar"],
            cwd=ruta_downloads,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

        # se le da tiempo para que arranque antes de continuar con Superflex
        time.sleep(8)

        # se confirma que efectivamente quedó corriendo
        resultado = subprocess.run(
            ["pgrep", "-f", "superflex-tray-icon.jar"],
            capture_output=True, text=True
        )
        if resultado.returncode != 0:
            mensaje = "Se intentó iniciar superflex-tray-icon.jar pero no quedó corriendo"
            log.error(mensaje)
            return False, mensaje

        log.info("superflex-tray-icon.jar iniciado correctamente")
        return True, "superflex-tray-icon.jar iniciado correctamente"

    except Exception as e:
        mensaje = f"Ocurrió un error al verificar/iniciar superflex-tray-icon.jar: {e}"
        log.error(mensaje)
        return False, mensaje

def _tomar_captura_error(page, log, ruta_capturas, nombre):
    # pantallazo del error para poder revisarlo después (mismo criterio que se usa
    # en insercion_datos_papeleria)
    ruta_captura = None
    try:
        os.makedirs(ruta_capturas, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        ruta_captura = os.path.join(ruta_capturas, f"error_{nombre}_{timestamp}.png")
        page.screenshot(path=ruta_captura, full_page=True)
        log.info(f"Pantallazo del error guardado en {ruta_captura}")
    except Exception as e_captura:
        log.error(f"No se pudo tomar el pantallazo del error: {e_captura}")
    return ruta_captura

def iniciar_sesion_superflex(page, URL_SUPERFLEX, URL_SUPERFLEX_HOME, USER_SUPERFLEX, PASS_SUPERFLEX, log=object, ruta_capturas=None):
    try:
        log.info("Iniciando sesión en Superflex")
        page.goto(f"{URL_SUPERFLEX}")
        page.wait_for_timeout(10000)  # Esperar 10 segundos para que la página se cargue completamente

        # USUARIO
        input_usuario = page.wait_for_selector('input[formcontrolname="usuario"]',state='visible', timeout=(10000))
        input_usuario.fill(str(USER_SUPERFLEX))

        # CONTRASEÑA
        input_pass = page.wait_for_selector('input[formcontrolname="contrasena"]',state='visible',timeout= (10000))
        input_pass.fill(str(PASS_SUPERFLEX))

        page.locator("button:has-text('ingresar')").click()

        page.wait_for_timeout(10000)
        page.wait_for_url(URL_SUPERFLEX_HOME, timeout=25000)
        log.info("Login exitoso en Superflex")
        return True, "Login exitoso en Superflex", None

    except PlaywrightTimeoutError:
        mensaje = "Error: Timeout al cargar la página de inicio de sesión de Superflex"
        log.error(mensaje)
        ruta_captura = _tomar_captura_error(page, log, ruta_capturas, "login_superflex")
        return False, mensaje, ruta_captura

    except Exception as e:
        mensaje = f"Ocurrio un error al iniciar sesión en superflex: {e}"
        log.error(mensaje)
        ruta_captura = _tomar_captura_error(page, log, ruta_capturas, "login_superflex")
        return False, mensaje, ruta_captura

def navegacion_menu_superflex(page, log=object, ruta_capturas=None):
    try:
        log.info("Inicia navegacion menu")
        page_buscador = page.wait_for_selector('a:has(span.layout-menuitem-text:has-text("PRODUCTO-SERVICIO"))', state='visible', timeout=(10000))
        page_buscador.click()

        menu_administracion = page.wait_for_selector('li.active-menuitem ul[role="menu"] a:has(span:has-text("ADMINISTRACIÓN"))', state= 'visible')
        menu_administracion.click()

        config_parametros = page.wait_for_selector('a:has(span.layout-menuitem-text:has-text("2-Configuración de parámetros"))',state='visible',timeout=10000)
        config_parametros.click()
        page.wait_for_timeout(10000)
        log.info("Navegación de menú exitosa en Superflex")
        return True, "Navegación de menú exitosa en Superflex", None

    except PlaywrightTimeoutError:
        mensaje = "Error: Timeout al cargar el menú de navegación de Superflex"
        log.error(mensaje)
        ruta_captura = _tomar_captura_error(page, log, ruta_capturas, "navegacion_menu_superflex")
        return False, mensaje, ruta_captura

    except Exception as e:
        mensaje = f"Ocurrio un error al navegar el menú en superflex: {e}"
        log.error(mensaje)
        log.error(traceback.format_exc())   # <-- agrega esta línea temporalmente
        ruta_captura = _tomar_captura_error(page, log, ruta_capturas, "navegacion_menu_superflex")
        return False, mensaje, ruta_captura

def insercion_datos_papeleria(page, log, registro, ruta_capturas):
    try:
        # ---------- LIMPIAR FORMULARIO ----------
        # el formulario no se reinicia solo entre un registro y otro (todavía no se hace
        boton_limpiar = page.locator('button:has-text("Limpiar")')
        boton_limpiar.wait_for(state='visible', timeout=10000)
        boton_limpiar.click()
        page.wait_for_timeout(2000)

        # ---------- PARÁMETRO ----------
        # MUEVE_PAPELERIA_SETA es un caso especial: en la página aparece como "MUEVE PAPELERIA"
        # (sin el sufijo SETA). El resto de parámetros se escriben normal, reemplazando "_" por espacio.
        parametro = registro.get("parametro")
        if parametro == "MUEVE_PAPELERIA_SETA":
            texto_parametro = "MUEVE PAPELERIA"
        else:
            texto_parametro = parametro.replace("_", " ")

        log.info(f"Inicia proceso de insercion de datos papeleria en administrar parametro (id={registro.get('id')}, parametro='{parametro}' -> '{texto_parametro}')")

        page_parametro = page.locator('p-dropdown:has-text("--SELECCIONE--") div.p-dropdown-trigger[role="button"]').first
        page_parametro.wait_for(state='visible', timeout=10000)
        page_parametro.click()

        # al abrir el dropdown de Parámetro el campo de búsqueda queda enfocado automáticamente
        page.wait_for_timeout(2000)
        page.keyboard.type(texto_parametro)
        page.wait_for_timeout(2000)

        opcion_parametro = page.locator(f'li.p-dropdown-item:text-is("{texto_parametro}")').first
        opcion_parametro.wait_for(state='visible', timeout=10000)
        # clic nativo por JS: el clic simulado de Playwright a veces no dispara el manejador
        # de Angular en estos <li> de PrimeNG y se queda colgado o no selecciona nada
        opcion_parametro.evaluate("el => el.click()")
        log.info(f"Parámetro '{texto_parametro}' seleccionado correctamente")

        # ---------- JERARQUÍA ----------
        # viene en mayúsculas en la BD (ej. "USUARIO") y en la página se ve como "Usuario".
        # Válido para valores de una sola palabra; si aparece un valor de varias palabras
        # (ej. PUNTO_VENTA -> "Punto de Venta") hay que revisar este mapeo puntualmente.
        jerarquia = registro.get("jerarquia")
        texto_jerarquia = jerarquia.capitalize()

        page_jerarquia = page.locator('p-dropdown:has-text("Seleccione una Jerarquía") div.p-dropdown-trigger[role="button"]').first
        page_jerarquia.wait_for(state='visible', timeout=10000)
        page_jerarquia.click()
        page.wait_for_timeout(2000)

        # este dropdown no tiene buscador, se hace clic directo en la opción
        # (Playwright hace scroll automático hasta el elemento si hace falta)
        opcion_jerarquia = page.locator(f'li.p-dropdown-item:text-is("{texto_jerarquia}")').first
        opcion_jerarquia.wait_for(state='visible', timeout=10000)
        opcion_jerarquia.evaluate("el => el.click()")
        log.info(f"Jerarquía '{texto_jerarquia}' seleccionada correctamente")

        # ---------- USUARIO (campo que se desbloquea cuando Jerarquía = Usuario) ----------
        # TODO: solo se maneja el caso Jerarquía = Usuario. Ciudad/Subzona/Oficina/Célula/
        # Punto de Venta desbloquean otro campo distinto que aún no está implementado.
        if jerarquia == "USUARIO":
            usuario_param = registro.get("usuario_param")
            log.info(f"Se busca el usuario con cédula '{usuario_param}'")

            boton_buscar_usuario = page.locator('input[placeholder="Buscar Usuario"]').locator('xpath=following-sibling::button[1]')
            boton_buscar_usuario.wait_for(state='visible', timeout=10000)
            boton_buscar_usuario.click()

            dialog_buscador = page.locator('div.p-dialog:has-text("Buscador Usuario")')
            dialog_buscador.wait_for(state='visible', timeout=10000)

            # el filtro de la columna "Cédula" es el primer input de filtro de la tabla
            filtro_cedula = dialog_buscador.locator('input.p-inputtext').first
            filtro_cedula.click()
            filtro_cedula.fill(str(usuario_param))
            filtro_cedula.press("Enter")
            page.wait_for_timeout(2500)

            radio_usuario = dialog_buscador.locator('p-tableradiobutton .p-radiobutton-box').first
            radio_usuario.wait_for(state='visible', timeout=10000)
            radio_usuario.click()
            log.info(f"Usuario con cédula '{usuario_param}' seleccionado correctamente")

        # ---------- CLASIFICACIÓN ----------
        # este dropdown sí tiene buscador (igual que Parámetro). Se busca lo que trae
        # el registro en `clasificacion`, reemplazando "_" por espacio (ej. VENTA_LOTERIA
        # -> "VENTA LOTERIA"). Algunos registros quemados traen clasificacion vacía, en
        # ese caso se omite el campo.
        clasificacion = registro.get("clasificacion")
        lista_subclasificaciones = None
        if clasificacion:
            texto_clasificacion = clasificacion.replace("_", " ")
            log.info(f"Se busca la clasificación '{clasificacion}' -> '{texto_clasificacion}'")

            page_clasificacion = page.locator('p-dropdown:has-text("--SELECCIONE--") div.p-dropdown-trigger[role="button"]').first
            page_clasificacion.wait_for(state='visible', timeout=10000)
            page_clasificacion.click()

            # al abrir el dropdown de Clasificación el campo de búsqueda queda enfocado automáticamente
            page.wait_for_timeout(2000)
            page.keyboard.type(texto_clasificacion)
            page.wait_for_timeout(2000)

            opcion_clasificacion = page.locator(f'li.p-dropdown-item:text-is("{texto_clasificacion}")').first
            opcion_clasificacion.wait_for(state='visible', timeout=10000)

            # se captura la lista de subclasificaciones que trae Superflex al seleccionar
            # la Clasificación: hay nombres repetidos (ej. "SUPERCHANCE" con dos códigos
            # distintos) y esta lista permite diferenciarlos más abajo.
            try:
                with page.expect_response(lambda r: "subclasificaciones/clasificacion" in r.url, timeout=10000) as respuesta_subclasificaciones:
                    opcion_clasificacion.evaluate("el => el.click()")
                lista_subclasificaciones = respuesta_subclasificaciones.value.json()
            except PlaywrightTimeoutError:
                log.warning("No llegó a tiempo la respuesta con la lista de subclasificaciones; si el registro pide una subclasificación con texto duplicado en la página, se podría seleccionar la incorrecta")

            log.info(f"Clasificación '{texto_clasificacion}' seleccionada correctamente")
        else:
            log.info("El registro no trae clasificación, se omite este campo")

        # ---------- SUBCLASIFICACIÓN ----------
        # mismo tipo de dropdown con buscador. A veces el registro trae subclasificacion
        # vacía, en ese caso se salta. Cuando viene con un número al inicio (ej.
        # "2049- SUPERCHANCE", "2802-SUPERCHANCE") ese número es el código real de la
        # subclasificación en Superflex y el resto (guion/espacios incluidos) se descarta
        # para armar el texto que se busca/escribe en el dropdown. Algunos registros traen
        # "_" en vez de espacio (ej. "CHANCE_DOBLE" -> "CHANCE DOBLE"), igual que en Clasificación.
        # CHANCE DOBLE es un caso especial: en la página la opción se llama "VENTA CHANCE DOBLE".
        subclasificacion = registro.get("subclasificacion")
        if subclasificacion:
            texto_subclasificacion = re.sub(r'^\d+[\s-]*', '', subclasificacion).strip().replace('_', ' ')
            if texto_subclasificacion == "CHANCE DOBLE":
                texto_subclasificacion = "VENTA CHANCE DOBLE"
            log.info(f"Se busca la subclasificación '{subclasificacion}' -> '{texto_subclasificacion}'")

            # con nombres repetidos (ej. dos "SUPERCHANCE"), se usa el código del registro
            # para calcular qué posición del dropdown le corresponde (0 = primera). Si no
            # se puede calcular, se usa 0 (comportamiento anterior).
            indice_opcion = 0
            match_codigo = re.match(r'^(\d+)', subclasificacion.strip())
            if match_codigo and lista_subclasificaciones:
                codigo_objetivo = match_codigo.group(1)
                ocurrencias_previas = 0
                encontrado = False
                for item in lista_subclasificaciones:
                    if item.get("descripcion") != texto_subclasificacion:
                        continue
                    if item.get("subClasificacion") == codigo_objetivo:
                        indice_opcion = ocurrencias_previas
                        encontrado = True
                        break
                    ocurrencias_previas += 1
                if not encontrado:
                    log.warning(f"El código '{codigo_objetivo}' no aparece en la lista de subclasificaciones de Superflex; se selecciona la primera opción visible con el texto '{texto_subclasificacion}'")
                elif indice_opcion > 0:
                    log.info(f"'{texto_subclasificacion}' está repetido en la página; se selecciona la opción #{indice_opcion + 1} (código {codigo_objetivo})")

            page_subclasificacion = page.locator('p-dropdown:has-text("--SELECCIONE--") div.p-dropdown-trigger[role="button"]').first
            page_subclasificacion.wait_for(state='visible', timeout=10000)
            page_subclasificacion.click()

            # al abrir el dropdown de Subclasificación el campo de búsqueda queda enfocado automáticamente
            page.wait_for_timeout(2000)
            page.keyboard.type(texto_subclasificacion)
            page.wait_for_timeout(2000)

            opcion_subclasificacion = page.locator(f'li.p-dropdown-item:text-is("{texto_subclasificacion}")').nth(indice_opcion)
            opcion_subclasificacion.wait_for(state='visible', timeout=10000)
            opcion_subclasificacion.evaluate("el => el.click()")
            log.info(f"Subclasificación '{texto_subclasificacion}' seleccionada correctamente")
        else:
            log.info("El registro no trae subclasificación, se omite este campo")

        # ---------- VALOR ----------
        # es un checkbox: si valor = "S" se marca, si valor = "N" se deja sin marcar
        # (el checkbox arranca sin marcar por defecto).
        valor = registro.get("valor")
        if valor == "S":
            checkbox_valor = page.locator('p-checkbox div.p-checkbox-box').first
            checkbox_valor.wait_for(state='visible', timeout=10000)
            checkbox_valor.click()
            log.info("Valor 'S', se marca el checkbox")
        elif valor == "N":
            log.info("Valor 'N', el checkbox se deja sin marcar")
        else:
            log.info(f"Valor '{valor}' no reconocido (se esperaba 'S' o 'N'), se deja el checkbox sin marcar")

        # ---------- GUARDAR ----------
        # el botón "Guardar" es #confirmarBtn (dentro del componente <sf-confirmar-btn>)
        boton_guardar = page.locator('#confirmarBtn')
        boton_guardar.wait_for(state='visible', timeout=10000)
        boton_guardar.click()
        page.wait_for_timeout(2000)

        # al guardar aparece un diálogo de confirmación de PrimeNG, hay que aceptarlo
        boton_aceptar = page.locator('button.p-confirm-dialog-accept')
        boton_aceptar.wait_for(state='visible', timeout=10000)
        boton_aceptar.click()
        page.wait_for_timeout(2000)
        log.info(f"Registro id={registro.get('id')} guardado correctamente")

        return True, f"Registro id={registro.get('id')} guardado correctamente", None

    except Exception as e:
        mensaje = f"Ocurrio un error al insertar los datos en el modulo {e}"
        log.error(mensaje)

        # se toma un pantallazo del error para poder revisarlo después
        ruta_captura = None
        try:
            os.makedirs(ruta_capturas, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            ruta_captura = os.path.join(ruta_capturas, f"error_papeleria_id{registro.get('id')}_{timestamp}.png")
            page.screenshot(path=ruta_captura, full_page=True)
            log.info(f"Pantallazo del error guardado en {ruta_captura}")
        except Exception as e_captura:
            log.error(f"No se pudo tomar el pantallazo del error: {e_captura}")

        # si quedó un dropdown/diálogo abierto, se cierra con Escape para que el
        # siguiente registro no choque con un overlay tapando el botón "Limpiar"
        try:
            page.keyboard.press("Escape")
            page.wait_for_timeout(1000)
        except Exception:
            pass
        return False, mensaje, ruta_captura