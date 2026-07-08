from src.settings.config import parametrizar_logs_y_ruta_archivos
from src.services.servicios_email import enviar_email
from src.settings.entorno import env
import json
from src.services.servicios_peticiones import verificar_url_emsa,consultar_grilla_emsa, validar_contenido_factura, descargar_pdf
from src.services.utils import obtener_fecha_actual, conectar_a_carpeta_compartida, verificar_carpeta_destino
from src.services.servicios_peticiones import verificar_url_emsa,descarga_facturas_emsa,descartar_emsa,finalizar_emsa,generar_excel_consolidado
from src.services.db import ejecutar_query

robot = "servicios_publicos"
log, ruta_descarga = parametrizar_logs_y_ruta_archivos(robot)

#CONTROL TOTAL AQUÍ
# MODO_LECTURA = "PDF"   # "XML" o "PDF"

if env.ENV == "dev":
    prefijo = "PRUEBAS"
else:
    prefijo = ""

destinatarios =[
    "auxanalista@consuerte.com.co",
    "asistenteadm@consuerte.com.co"
]

destinatario_propio = ["auxanalista@consuerte.com.co"]

asunto = f"{prefijo} EJECUCION PROCESO SERVICIOS PUBLICOS"
titulo_mensaje = f"{prefijo} ROBOT SERVICIOS PUBLICOS"
mensaje = "se notifica la ejecucion del proceso automatico de servicios publicos:<br><br>"

# URLS
URL_HOME_EMSA = env.URL_HOME_EMSA
URL_GRILLA = env.URL_GRILLA
URL_DESCARGAR_PDF_EMSA = env.URL_DESCARGAR_PDF_EMSA
URL_FINALIZAR_EMSA = env.URL_FINALIZAR_EMSA
URL_DESCARTAR_EMSA = env.URL_DESCARTAR_EMSA
URL_COMPARTIDA= env.URL_COMPARTIDA
USER_COMPARTIDA = env.USER_COMPARTIDA
PASS_COMPARTIDA = env.PASS_COMPARTIDA
IP_COMPARTIDA = env.IP_COMPARTIDA

def main():
    global mensaje

    # ---------------verificamos que el sitio esta activo------------
    disponible, motivo = verificar_url_emsa(URL_HOME_EMSA, log)
    if not disponible:
        mensaje += f"el sitio emsa no esta disponible: {motivo}<br>"
        log.error(f"proceso detenido {motivo}")
        enviar_email(
            destinatario=destinatarios,
            asunto=asunto,
            mensaje=f"{mensaje}<br><br>",
            titulo_mensaje=titulo_mensaje,
            prioridad=1
        )
        return

    log.info(f"Sitio disponible.")
    # ---------
    log.info("Se procede a consultar la grilla")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0",
        "Accept": "*/*",
        "Origin": "http://10.231.0.137",
        "Connection": "keep-alive",
        "Referer": "http://10.231.0.137/"
        # Eliminamos Content-Length y dejamos que requests lo maneje
    }

    codigos_cliente = consultar_grilla_emsa(url=URL_GRILLA, headers=headers, log=log)

    log.info(f"respuesta de la funcion: {codigos_cliente}")
    log.info(f"tipo de dato recibido: {type(codigos_cliente)}")

    codigos_cliente = json.loads(codigos_cliente)
    # codigos_cliente = [{"codigo":"1296268461","pdv":"2260-PORFIA 2","valor":"168372","fecha_venc":"2026-05-14","carpeta":"VILLAVICENCIO"},{"codigo":"130940049","pdv":"2259-PORFIA 1","valor":"139522","fecha_venc":"2026-05-14","carpeta":""},{"codigo":"131264425","pdv":"3355-ESPECIALIZADO PORFIA","valor":"902627","fecha_venc":"2026-05-14","carpeta":"VILLAVICENCIO"},{"codigo":"200528807","pdv":"2220-AMERICAS","valor":"233858","fecha_venc":"2026-05-14","carpeta":"VILLAVICENCIO"}]#,{"codigo":"235649105","pdv":"1363-CAMILO TORRES","valor":"55590","fecha_venc":"2026-05-13","carpeta":"GRANADA"},{"codigo":"237218351","pdv":"3609-LA 13 BELEN","valor":"86220","fecha_venc":"2026-05-13","carpeta":"GRANADA"},{"codigo":"240312990","pdv":"1678-CASINO EL DORADO","valor":"60610","fecha_venc":"2026-05-13","carpeta":"GRANADA"},{"codigo":"241393808","pdv":"1367-LA CATEDRA","valor":"66420","fecha_venc":"2026-05-13","carpeta":"GRANADA"},{"codigo":"243506330","pdv":"1176-PRINCIPAL 1 GRANADA","valor":"1058180","fecha_venc":"2026-05-13","carpeta":"GRANADA"},{"codigo":"305556364","pdv":"1361-HOTEL CORDILLERA","valor":"127050","fecha_venc":"2026-05-13","carpeta":"GRANADA"},{"codigo":"340283152","pdv":"3582-PORFIA 7","valor":"172010","fecha_venc":"2026-05-14","carpeta":"VILLAVICENCIO"},{"codigo":"368949423","pdv":"4058-OFICINA PORFIA 5","valor":"195786","fecha_venc":"2026-05-14","carpeta":"VILLAVICENCIO"},{"codigo":"371333644","pdv":"2258-PLAYA RICA","valor":"121480","fecha_venc":"2026-05-14","carpeta":"VILLAVICENCIO"},{"codigo":"401062503","pdv":"3402-OFICINA LA MADRID 3","valor":"246535","fecha_venc":"2026-05-14","carpeta":"VILLAVICENCIO"},{"codigo":"407711134","pdv":"3049-PORFIA 6","valor":"116462","fecha_venc":"2026-05-14","carpeta":"VILLAVICENCIO"},{"codigo":"414495233","pdv":"1406-BILLARES RICAUTE GRANADA","valor":"85080","fecha_venc":"2026-05-13","carpeta":"GRANADA"},{"codigo":"415143772","pdv":"1474-VILLA OLIMPICA - GRANADA","valor":"100960","fecha_venc":"2026-05-13","carpeta":"GRANADA"},{"codigo":"460421101","pdv":"4067-HOSPITAL GRANADA","valor":"333520","fecha_venc":"2026-05-13","carpeta":"GRANADA"},{"codigo":"462569528","pdv":"4089-LA NOVENA","valor":"49030","fecha_venc":"2026-05-13","carpeta":"GRANADA"},{"codigo":"464122113","pdv":"4043-CENTRO COMERCIAL MADRID RESERVADO E2","valor":"204910","fecha_venc":"2026-05-14","carpeta":"VILLAVICENCIO"},{"codigo":"661736903","pdv":"2216-LA NOHORA","valor":"134398","fecha_venc":"2026-05-14","carpeta":"VILLAVICENCIO"}]

    if not codigos_cliente:
        log.info(f"la grilla esta vacia, se termina el proceso: {codigos_cliente}")
        mensaje += f"Se evidencia que no hay registros en la grilla: {codigos_cliente}<br><br> Se cancela la ejecución."
        enviar_email(
            destinatario=destinatarios,
            asunto=asunto,
            mensaje=f"{mensaje}<br><br>",
            titulo_mensaje=titulo_mensaje,
            prioridad=1
        )
        return

    # cont = 0
    # lista para los consolidados
    facturas_procesadas = []
    facturas_no_procesadas = []
    sin_carpeta_destino =[]

    for item in codigos_cliente:
        # if cont == 1:
        #     log.info("fin del for")
        #     break

        cod_cliente = item.get("codigo")
        pdv = item.get("pdv")
        carpeta = item.get("carpeta")
        valor_pago = item.get("valor")
        fecha_pago = item.get("fecha_venc")

        log.info(f"Código: {cod_cliente}")
        log.info(f"PDV: {pdv}")
        log.info(f"Valor: {valor_pago}")
        log.info(f"Fecha: {fecha_pago}")
        log.info(f"Carpeta: {carpeta}")
        log.info("------")

        log.info(f"se procede a descargar la siguiente factura: {cod_cliente}")

        url_descarga_pdf = URL_DESCARGAR_PDF_EMSA+cod_cliente
        # url_descarga_pdf = "https://www.emsa-esp.com.co:441/factura/consulta_factura.php?cuenta=123456789"

        log.info(f"url de descarga del pdf {url_descarga_pdf}")

        content = descarga_facturas_emsa(url_descarga_pdf)

        log.info(f"content: {content}")


        # COMPROBAR SI TIENE CARPETA DESTINO EN LA GRILLA
        if carpeta == "":
            titulo_mensaje_factura = f"FACTURA SIN PARAMETRIZAR"
            carpeta = "PARAMETRIZAR"
            mensaje += f"Se informa que la factura {cod_cliente} - {pdv} no se encuentra con la carpeta parametrizada, según se muestra en la grilla. Debido a esto la factura se movera a la carpeta {carpeta}.<br><br> Por favor se solicita revisar y realizar su respectivo proceso de parametrización. <br><br> Fecha de consulta {obtener_fecha_actual()} .<br>"
            log.error(f"Se informa que la factura {cod_cliente} - {pdv} no se encuentra con la carpeta parametrizada, según se muestra en la grilla")
            log.error(f"Por defecto se mueve a la carpeta {carpeta}")
            # enviar_email(
            #     destinatario=destinatarios,
            #     asunto=asunto,
            #     mensaje=f"{mensaje}<br><br>",
            #     titulo_mensaje=titulo_mensaje_factura,
            #     prioridad=1
            # )
            # guardar puntos sin carpeta parametrizada
            sin_carpeta_destino.append({
                "codigo_cliente": cod_cliente,
                "punto_venta": pdv,
                "carpeta": carpeta,
                "valor_pago": valor_pago,
                "fecha_pago": fecha_pago,
                "Novedad": "carpeta destino no parametrizada"
            })
            # return

    
        # VALIDAR ACCESO A LA COMPARTIDA
        if not conectar_a_carpeta_compartida(servidor=IP_COMPARTIDA, usuario=env.USER_COMPARTIDA, contraseña=env.PASS_COMPARTIDA, log=log):
            titulo_mensaje_compratida = f"SIN ACCESO A LA COMPARTIDA"
            mensaje += f"No se pudo establecer conexión con la carpeta compartida {URL_COMPARTIDA}. Se verifica que la carpeta exista y que las credenciales sean correctas.<br>"
            log.error(f"No se pudo establecer conexión con la carpeta compartida {URL_COMPARTIDA}")
            enviar_email(
                destinatario=destinatarios,
                asunto=f"ERROR {asunto}",
                mensaje=f"{mensaje}<br><br>",
                titulo_mensaje=titulo_mensaje_compratida,
                prioridad=1
            )
            return


        # VALIDAR QUE LA CARPETA DESTINO EXISTA
        log.info("Se procede a validar que la carpeta destino exista en la compartida")
        carpeta_destino = f"{URL_COMPARTIDA}{carpeta}"

        if not verificar_carpeta_destino(carpeta_destino=carpeta_destino, log=log):
            titulo_mensaje_carpeta = f"ERROR AL VERIFICAR O CREAR LA CARPETA DESTINO"
            mensaje += f"Ocurrio un error al verificar o crear la carpeta destino {carpeta_destino} en la compartida. Se verifica que la carpeta exista para continuar con el proceso.<br>"
            enviar_email(
                destinatario=destinatarios,
                asunto=f"ERROR {asunto}",
                mensaje=f"{mensaje}<br><br>",
                titulo_mensaje=titulo_mensaje_carpeta,
                prioridad=1
            )

        # VALIDAR TIPO DE CONTENIDO DE LA PETICION REQUEST A LA FACTURA
        # codigo = "123456789"  # Ejemplo de código de cliente
        url_descarga_pdf = URL_DESCARGAR_PDF_EMSA + cod_cliente
        nombre_pdf = f"{cod_cliente}-{pdv}".replace("/", "-").replace("\\", "-").replace(":", "").replace("*", "").replace("?", "").replace('"', "").replace("<", "").replace(">", "").replace("|", "")
        content = validar_contenido_factura(url_descarga_pdf, log)
        log.info(f"content: {content}")


        if content != "application/pdf":
            mensaje += f"El contenido obtenido no es un PDF válido para el código {cod_cliente}. Se recibió: {content}<br>"
            log.error(f"Contenido no válido para código {cod_cliente}: {content}")
            # enviar_email(
            #     destinatario=destinatarios,
            #     asunto=asunto,
            #     mensaje=f"{mensaje}<br><br>",
            #     titulo_mensaje=titulo_mensaje,
            #     prioridad=1
            # )

        # DESCARGAR PDF DIRECTAMENTE EN LA COMPARTIDA
        ruta_descarga_compartida = carpeta_destino
        log.info("asd")
        log.info(url_descarga_pdf)
        log.info(nombre_pdf)
        log.info(ruta_descarga_compartida)
        log.info("Iniciando descarga del PDF...")
        ruta_pdf, mensaje_pdf, estado_compartida = descargar_pdf( 
            url=url_descarga_pdf,
            nombre_pdf=nombre_pdf,
            ruta_descarga=ruta_descarga_compartida,
            log=log
        )

        #ERROR AL DESCARGAR EL PDF EN LA COMPARTIDA
        if ruta_pdf is None:
            # titulo_mensaje = "ERROR AL DESCARGAR PDF EN LA COMPARTIDA"
            log.error(mensaje_pdf)
            mensaje += f"Error al descargar el PDF para el código {cod_cliente}: {mensaje_pdf}<br>"
            # enviar_email(
            #     destinatario=destinatarios,
            #     asunto=f"ERROR {asunto}",
            #     mensaje=f"{mensaje}<br><br>",
            #     titulo_mensaje=titulo_mensaje,
            #     prioridad=1
            # )

            headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0",
            "Accept": "*/*",
            "Origin": "http://10.231.0.137",
            "Connection": "keep-alive",
            "Referer": "http://10.231.0.137/"
            }
        
            resultado_descarte = descartar_emsa(
                url=URL_DESCARTAR_EMSA,log=log,
                headers=headers,
                codigo=cod_cliente,
                punto_venta=pdv.split("-")[0].strip(), #sirve para exytraer solo el numero
                novedad= f"NO DESCARGADO"
                )
            
            # guardar puntos no procesados
            facturas_no_procesadas.append({
                "codigo_cliente": cod_cliente,
                "punto_venta": pdv,
                "carpeta": carpeta,
                "valor_pago": valor_pago,
                "fecha_pago": fecha_pago,
                "estado": "NO DESCARGADO"
            })

        
            if resultado_descarte is None:
                log.error(f"no se pudo descartar la factura{cod_cliente} en la grilla")
                # enviar_email(
                #     destinatario=destinatarios,
                #     asunto=f"ERROR{asunto}",
                #     mensaje=f"no se pudo descartar la factura {cod_cliente} - {pdv} en la grilla.<br><br>",
                #     titulo_mensaje=titulo_mensaje,
                #     prioridad=1
                # )


        # ULTIMA VALIDACION DE QUE EL PDF SE DESCARGO CORRECTAMENTE
        #EL PDF SE DESCARGO CORRECTAMENTE
        if ruta_pdf is not None and estado_compartida:

            estado_factura = "DESCARGADA"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0",
                "Accept": "*/*",
                "Origin": "http://10.231.0.137",
                "Connection": "keep-alive",
                "Referer": "http://10.231.0.137/"
                }
            
            resultado_finalizado= finalizar_emsa(
                url=URL_FINALIZAR_EMSA,
                log=log,
                headers=headers,
                codigo=cod_cliente,
                punto=pdv.split("-")[0].strip(),
                fecha=fecha_pago,
                valor=valor_pago,
                novedad=estado_factura
            )

            # GUARDAR FACTURA PROCESADA 
            facturas_procesadas.append({
                "codigo_cliente": cod_cliente,
                "punto_venta": pdv,
                "carpeta": carpeta,
                "valor_pago": valor_pago,
                "fecha_pago": fecha_pago,
                "estado": "DESCARGADO"
            })

            if resultado_finalizado is None:
                log.error(f"no se pudo finalizar la factura {cod_cliente} en la grilla")
                enviar_email(
                    destinatario=destinatarios,
                    asunto=f"ERROR {asunto}",
                    mensaje=f"No se pudo finalizar la factura {cod_cliente} - {pdv} en la grilla.<br><br>",
                    titulo_mensaje=titulo_mensaje,
                    prioridad=1
                )


        # REGISTRAR EN BASE DE DATOS
        sql = "INSERT INTO robot_servicios_publicos (codigo_cliente, punto_venta, carpeta, valor_pago, fecha_pago, compartida, estado) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        ejecutar_query(sql, (cod_cliente, pdv, carpeta, valor_pago, fecha_pago, estado_compartida, estado_compartida))

    log.info("=== Proceso finalizado ===")

    # generar consolidado de procesados
    archivos_procesados = generar_excel_consolidado(
        datos=facturas_procesadas,
        ruta_descarga=ruta_descarga,
        nombre_archivo="consolidado_puntos_procesados.xlsx",
        log=log
        )
    
    if archivos_procesados is None:
        mensaje_error="no se pudo generar el consolidado de los puntos procesados<br><br>"
        enviar_email(
            destinatario=destinatarios,
            asunto=f"ERROR {asunto}",
            mensaje=mensaje_error,
            titulo_mensaje=titulo_mensaje,
            prioridad=1
        )
        return
    log.info("Enviando archivo de puntos procesados")
    enviar_email(
        destinatario=destinatarios,
        asunto=asunto,
        mensaje=f"Me permito adjuntar archivo Excel con los datos de los Códigos de los Clientes consultados de la página de la EMSA.<br><br>",
        titulo_mensaje=titulo_mensaje,
        adjuntos=archivos_procesados
    )

    # generar consolidado no procesados
    archivos_no_procesados= generar_excel_consolidado(
        datos=facturas_no_procesadas,
        ruta_descarga=ruta_descarga,
        nombre_archivo="consolidado_puntos_no_procesados.xlsx",
        log=log
        )
    if archivos_no_procesados is None:
        mensaje_error="no se pudo generar el consolidado de los puntos no procesados<br><br>"
        enviar_email(
            destinatario=destinatarios,
            asunto=f"ERROR {asunto}",
            mensaje=mensaje_error,
            titulo_mensaje=titulo_mensaje,
            prioridad=1
        )
        return
    log.info("Enviando archivo de puntos no procesados")
    enviar_email(
        destinatario=destinatario_propio,
        asunto=asunto,
        mensaje=f"Me permito adjuntar archivo Excel con los datos de los Códigos no consultados de la página de la EMSA.<br><br>",
        titulo_mensaje=titulo_mensaje,
        adjuntos=archivos_no_procesados
    )

    # generar consolidado carpeta no parametrizada
    parametrizar_carpeta=generar_excel_consolidado(
        datos=sin_carpeta_destino,
        ruta_descarga=ruta_descarga,
        nombre_archivo="Puntos sincarpeta parametrizada.xlsx",
        log=log
    )
    log.info("Enviando archivo de puntos sin carpeta parametrizada")
    enviar_email(
        destinatario=destinatario_propio,
        asunto=asunto,
        mensaje=f"Me permito adjuntar archivo Excel con los puntos sin carpeta parametrizada.<br><br>",
        titulo_mensaje=titulo_mensaje,
        adjuntos=parametrizar_carpeta,
        prioridad=1
    )


if __name__ == "__main__":
    main()