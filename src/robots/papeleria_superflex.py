import json
import os
import subprocess
import traceback
from datetime import datetime
from src.settings.config import parametrizar_logs_y_ruta_archivos
from src.services.servicios_email import enviar_email
from src.services.login_superflex  import iniciar_sesion_superflex, navegacion_menu_superflex, insercion_datos_papeleria, asegurar_tray_icon_superflex
from src.settings.entorno import env
from src.services.browser import open_browser
from src.services.db import ejecutar_query, ejecutar_query_dict

URL_SUPERFLEX = env.URL_SUPERFLEX
URL_SUPERFLEX_HOME = env.URL_SUPERFLEX_HOME
USER_SUPERFLEX = env.USER_SUPERFLEX
PASS_SUPERFLEX = env.PASS_SUPERFLEX


robot = "papeleria_superflex"
log,ruta_descarga = parametrizar_logs_y_ruta_archivos(robot)

if env.ENV == "dev":
    prefijo = "PRUEBAS"
else:
    prefijo = ""

destinatarios = [
    "auxanalista@consuerte.com.co"
]

asunto = f"{prefijo} EJECUCIÓN PROCESO PAPELERIA SUPERFLEX"
titulo_mensaje = f"{prefijo} ROBOT PAPELERIA SUPERFLEX"
mensaje = "Se notifica la ejecución del proceso automatico papeleria superflex:<br><br>"

def _otra_instancia_corriendo():
    """
    Revisa si ya hay otro proceso de este mismo robot corriendo (ej. si el cron
    lo volvió a disparar mientras la corrida anterior todavía no termina de
    procesar cédulas en Superflex). Devuelve la lista de PIDs encontrados
    aparte del propio (vacía si no hay ninguno más corriendo).
    """
    propio_pid = os.getpid()
    resultado = subprocess.run(
        ["pgrep", "-f", "src.robots.papeleria_superflex"],
        capture_output=True, text=True
    )
    pids = [int(p) for p in resultado.stdout.split() if p.isdigit()]
    return [p for p in pids if p != propio_pid]

def main():
    log.info("SE INICIA EL PROCESO DE PAPELERIA SUPERFLEX")

    # se valida primero que no haya otra corrida de este robot ya en curso, para
    # no interrumpirla abriendo una segunda sesión de Superflex al mismo tiempo
    otros_pids = _otra_instancia_corriendo()
    if otros_pids:
        mensaje_skip = (
            f"Ya hay otra instancia de este robot corriendo (PID {otros_pids}), "
            "se cancela esta ejecución para no interrumpir el proceso en curso en Superflex."
        )
        log.info(mensaje_skip)
        enviar_email(
            destinatario=destinatarios,
            mensaje=f"{mensaje}{mensaje_skip}<br><br>",
            asunto=asunto,
            titulo_mensaje=titulo_mensaje,
            prioridad=3)
        return

    # subcarpeta con el día y hora de esta ejecución, donde quedarán agrupados
    # todos los pantallazos de error que se tomen en esta corrida
    ruta_capturas_ejecucion = os.path.join(ruta_descarga, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

    try:
        # ------- Se consultan los parámetros pendientes por cargar en BNET -------
        log.info("Se consultan los parámetros pendientes de cargue (estado = 0)")
        parametros_pendientes = ejecutar_query_dict("SELECT * FROM cargue_parametros_papeleria WHERE estado = %s order by tipo_parametro desc",('0',))

        # se guardan los datos de la consulta como json (fecha_sys viene como datetime y no es serializable directo)
        codigos_papeleria = json.loads(json.dumps(parametros_pendientes, default=str))

        # DATOS QUEMADOS PARA PRUEBAS: mientras se construye el ingreso a BNET se trabaja con este lote fijo
        # en vez del resultado de la consulta. Quitar/comentar esta línea para volver a usar los datos reales.
        # codigos_papeleria = []

        if not codigos_papeleria:
            log.info("No se encontraron parámetros pendientes por cargar, se finaliza el proceso")
            enviar_email(
                destinatario=destinatarios,
                mensaje=f"{mensaje}No se encontraron parámetros pendientes por cargar en BNET.<br><br>",
                asunto=asunto,
                titulo_mensaje=titulo_mensaje,
                prioridad=3)
            return

        log.info(f"Se encontraron {len(codigos_papeleria)} parámetros pendientes por cargar")
        for i, parametro in enumerate(codigos_papeleria, start=1):
            log.info(f"Registro {i}: {parametro}")

        tray_ok, mensaje_local = asegurar_tray_icon_superflex(log=log)
        if not tray_ok:
            enviar_email(
                destinatario=destinatarios,
                mensaje=f"{mensaje}{mensaje_local}",
                asunto=f"ERORR {asunto}",
                titulo_mensaje=titulo_mensaje,
                prioridad=1)
            return

        # workspace=1 -> segundo espacio de trabajo (0 sería el primero), para no
        # aparecer encima de lo que el usuario esté usando en su escritorio actual
        page = open_browser(headless=False, workspace=1, log=log)


        login_ok, mensaje_local, ruta_captura_login = iniciar_sesion_superflex(page, URL_SUPERFLEX, URL_SUPERFLEX_HOME, USER_SUPERFLEX, PASS_SUPERFLEX, log=log, ruta_capturas=ruta_capturas_ejecucion)
        if not login_ok:
            enviar_email(
                destinatario=destinatarios,
                mensaje=f"{mensaje}{mensaje_local}",
                asunto=f"ERORR {asunto}",
                titulo_mensaje=titulo_mensaje,
                prioridad=1,
                adjuntos=[ruta_captura_login] if ruta_captura_login else None)
            return

        nav_ok, mensaje_local, ruta_captura_nav = navegacion_menu_superflex(page, log=log, ruta_capturas=ruta_capturas_ejecucion)
        if not nav_ok:
            enviar_email(
                destinatario=destinatarios,
                mensaje=f"{mensaje}{mensaje_local}",
                asunto=f"ERORR {asunto}",
                titulo_mensaje=titulo_mensaje,
                prioridad=1,
                adjuntos=[ruta_captura_nav] if ruta_captura_nav else None)
            return

        # se recorre cada registro y se selecciona su parámetro en Superflex, uno por uno
        procesados = []
        errores = []
        capturas_error = []
        for i, registro in enumerate(codigos_papeleria, start=1):
            log.info(f"Procesando registro {i}/{len(codigos_papeleria)} (id={registro.get('id')})")
            insercion_ok, mensaje_insercion, ruta_captura = insercion_datos_papeleria(page, log=log, registro=registro, ruta_capturas=ruta_capturas_ejecucion)
            if not insercion_ok:
                log.error(f"No se pudo procesar el registro id={registro.get('id')}: {mensaje_insercion}")
                errores.append(f"id={registro.get('id')} (cédula {registro.get('usuario_param')}): {mensaje_insercion}")
                if ruta_captura:
                    capturas_error.append(ruta_captura)
                continue

            # se guardó correctamente en Superflex/BNET: se marca el registro como procesado (estado = 2)
            try:
                ejecutar_query(
                    "UPDATE cargue_parametros_papeleria SET estado = %s WHERE id = %s",
                    ('2', registro.get('id'))
                )
                log.info(f"Registro id={registro.get('id')} actualizado a estado = 2 en la base de datos")
                procesados.append(registro)
            except Exception as e_db:
                log.error(f"Registro id={registro.get('id')} se guardó en Superflex pero no se pudo actualizar su estado en la base de datos: {e_db}")
                errores.append(f"id={registro.get('id')} (cédula {registro.get('usuario_param')}): se guardó en Superflex pero falló la actualización de estado en BD: {e_db}")

        # ------- correo final: siempre se envía, con la tabla de cédulas procesadas y,
        # si aplica, el detalle de los registros que no se pudieron procesar -------
        log.info(f"Proceso finalizado: {len(procesados)}/{len(codigos_papeleria)} registro(s) procesado(s) correctamente, {len(errores)} error(es)")

        tabla_procesados = ""
        if procesados:
            columnas = ("id", "usuario_param", "parametro", "jerarquia", "clasificacion", "subclasificacion", "valor")
            encabezados = ("ID", "Cédula", "Parámetro", "Jerarquía", "Clasificación", "Subclasificación", "Valor")
            filas = "".join(
                "<tr>" + "".join(
                    f"<td style='padding:4px 8px;border:1px solid #ccc;'>{reg.get(col) or '-'}</td>"
                    for col in columnas
                ) + "</tr>"
                for reg in procesados
            )
            encabezado_html = "".join(f"<th style='padding:4px 8px;border:1px solid #ccc;'>{h}</th>" for h in encabezados)
            tabla_procesados = (
                "<table style='border-collapse:collapse;width:100%;font-size:14px;'>"
                f"<tr style='background-color:#f0f0f0;'>{encabezado_html}</tr>"
                f"{filas}"
                "</table>"
            )

        mensaje_final = (
            "Se finalizó el proceso de papelería Superflex.<br><br>"
            f"Registros procesados correctamente: {len(procesados)}/{len(codigos_papeleria)}<br><br>"
        )
        if tabla_procesados:
            mensaje_final += f"{tabla_procesados}<br><br>"

        if errores:
            mensaje_errores = "<br>".join(errores)
            mensaje_final += (
                f"Se presentaron errores al procesar {len(errores)} registro(s) de papelería "
                f"(no quedaron procesados, revisar el/los pantallazo(s) adjunto(s)):<br><br>{mensaje_errores}<br><br>"
            )

        enviar_email(
            destinatario=destinatarios,
            mensaje=f"{mensaje}{mensaje_final}",
            asunto=f"{'ERROR ' if errores else ''}{asunto}",
            titulo_mensaje=titulo_mensaje,
            prioridad=1 if errores else 3,
            adjuntos=capturas_error if capturas_error else None)

    except Exception as e:
        # red de seguridad general: cualquier falla no prevista (conexión a BD, apertura
        # del navegador, etc.) se loguea y se avisa por correo en vez de morir en silencio
        log.error(f"Fallo inesperado en el proceso de papelería Superflex: {e}")
        log.error(traceback.format_exc())
        enviar_email(
            destinatario=destinatarios,
            mensaje=f"{mensaje}Ocurrió un error inesperado y el proceso se detuvo: {e}<br><br>",
            asunto=f"ERROR {asunto}",
            titulo_mensaje=titulo_mensaje,
            prioridad=1)


if __name__ == "__main__":
    main()