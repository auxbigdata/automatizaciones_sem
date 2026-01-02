import smtplib
from email.message import EmailMessage
import mimetypes
import os
import imaplib
import email
from email.header import decode_header
import os
import socket
import ssl
def enviar_email(destinatario: str, mensaje: str, asunto: str, titulo_mensaje: str, prioridad: int=0, adjuntos: str =None):
    mensaje = mensaje
    titulo_mensaje = titulo_mensaje
    plantilla = f"""<head>  
    <meta charset="utf-8">  
    <meta name="viewport" content="width=device-width,initial-scale=1">  
    <meta name="x-apple-disable-message-reformatting">  
    <title></title>  
    <style>  
        table, td, div, h1, p {{  
        font-family: Arial, sans-serif;  
        }}  
        @media screen and (max-width: 530px) {{  
        .unsub {{  
            display: block;  
            padding: 8px;  
            margin-top: 14px;  
            border-radius: 6px;  
            background-color: #555555;  
            text-decoration: none !important;  
            font-weight: bold;  
        }}  
        .col-lge {{  
            max-width: 100% !important;  
        }}  
        }}  
        @media screen and (min-width: 531px) {{  
        .col-sml {{  
            max-width: 27% !important;  
        }}  
        .col-lge {{  
            max-width: 73% !important;  
        }}  
        }}  
    </style>  
    </head>  
    <body style="margin:0;padding:0;word-spacing:normal;background-color:#939297;">  
    <div role="article" aria-roledescription="email" lang="en" style="text-size-adjust:100%;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;background-color:#1086FF;"> 
        <table role="presentation" style="width:100%;border:none;border-spacing:0;">  
        <tr>  
            <td align="center" style="padding:0;">    
            <table role="presentation" style="width:94%;max-width:600px;border:none;border-spacing:0;text-align:left;font-family:Arial,sans-serif;font-size:16px;line-height:22px;color:#363636;"> 
                <tr>  
                <td style="padding:40px 30px 30px 30px;text-align:center;font-size:24px;font-weight:bold;">  
                </td>  
                </tr>  
                <tr>  
                <td style="padding:30px;background-color:#ffffff;">  
                    <h1 style="margin-top:0;margin-bottom:16px;font-size:26px;line-height:32px;font-weight:bold;letter-spacing:-0.02em;"> 

    {titulo_mensaje}
    </h1>  
                    <p style="margin:0;"> 
                    
    Cordial saludo,
    <br><br>
    {mensaje}
    </div>  
                </td>  
                </tr>  
                </tr>  
                <tr>  
                <td style="padding:30px;background-color:#ffffff;">  
                    <p style="margin:0;">Cordialmente,  
    <br><br><br>
                    Automatización Robotica de Procesos Consuerte
                    <br>
                    auxanalista@consuerte.com.co 
    </p>
                </td>  
                </tr>  
                <tr>  
                <td style="padding:30px;text-align:center;font-size:12px;background-color:#404040;color:#cccccc;">  
                    <p style="margin:0;font-size:14px;line-height:20px;">&reg; Consuerte Villavicencio - Meta<br><a class="unsub" href="https://www.consuerte.com.co" style="color:#cccccc;text-decoration:underline;">Dirección: Calle 15 N° 40 - 01 Centro Comercial Primavera Urbana - Oficina 1001 
                    Teléfono: (608) 670 98 98 - 320 831 42 93</a></p>  
                </td>  
                </tr>  
            </table>   
            </td>  
        </tr>  
        </table>  
    </div>  
    </body>  
    </html> 
    """ 

    remitente = "auxanalista@consuerte.com.co"
    password = "C0nsu324*"
    msg = EmailMessage()
    msg["From"] = remitente
    msg["To"] = destinatario
    msg["Subject"] = asunto

    # enviar correo como importante
    if prioridad == 1:
        msg["Importance"] = "High"
        msg["X-Priority"] = "1"
        msg["X-MSMail-Priority"] = "High"

    msg.set_content(plantilla, subtype="html")

    # ==============================
    # Adjuntar archivos si existen
    # ==============================
    if adjuntos is not None:

        # Si viene un solo archivo, lo convertimos en lista
        if isinstance(adjuntos, str):
            adjuntos = [adjuntos]

        for ruta in adjuntos:
            if not os.path.isfile(ruta):
                raise FileNotFoundError(f"Adjunto no encontrado: {ruta}")

            tipo, encoding = mimetypes.guess_type(ruta)
            if tipo is None:
                tipo = "application/octet-stream"

            maintype, subtype = tipo.split("/", 1)

            with open(ruta, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype=maintype,
                    subtype=subtype,
                    filename=os.path.basename(ruta)
                )

    smtp = smtplib.SMTP("10.1.1.1", 587)
    smtp.login(remitente, password)
    smtp.send_message(msg)
    smtp.quit()

def descargar_adjuntos_por_asunto(imap_server: str, email_user: str,email_password: str,asunto_buscado: str,carpeta_descarga: str, log, etiqueta_correo: str = None):
    # ESTA FUNCION PROCESA SOLO UN CORREO SIN LEER A LA VEZ, DESDE EL PRIMERO EN LLEGAR HASTA EL ULTIMO EN LLEGAR
    try:
        log.info("Conectando con servidor de correo para descargar adjuntos:")
        log.info(f"Servidor IMAP: {imap_server}")
        log.info(F"Correo: {email_user}")
        log.info(f"Contraseña: {email_password}")
        log.info(f"Asunto: {asunto_buscado}")
        log.info(f"Carpeta de descarga de archivos adjuntos: {carpeta_descarga}")
        log.info(f"Etiqueta para mover el correo: {etiqueta_correo}")

        ruta_adjuntos_descargados = []
        nombre_adjuntos_descargados = []
        os.makedirs(carpeta_descarga, exist_ok=True)

        # Conexión IMAP
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_password)

        status, _ = mail.select("inbox")
        if status != "OK":
            log.error(f"Ocurrio un error al seleccionar inbox(bandeja de entrada) de la cuenta de correo especificada: {email_user}")
            return False, f"Ocurrio un error al seleccionar inbox(bandeja de entrada) de la cuenta de correo especificada: {email_user}", False

        log.info("Buscando correo...")
        # Buscar correos UNSEEN por asunto
        status, mensajes = mail.search(
            None, 'UNSEEN', 'SUBJECT', f'"{asunto_buscado}"'
        )

        if status != "OK":
            log.error("Ocurrió un error al realizar la búsqueda")
            return False, "Ocurrió un error al realizar la búsqueda", False

        ids_correos = mensajes[0].split()
        if not ids_correos:
            log.error("No se encontraron correos nuevos(sin leer) en la busqueda")
            return False, "No se encontraron correos nuevos(sin leer) en la busqueda", False

        # log.info(f"Correos encontrados: {len(ids_correos)}")
        mail_id = ids_correos[0]
            # adjuntos = False 
        try:
            status, datos = mail.fetch(mail_id, "(BODY.PEEK[])")
            if status != "OK":
                log.error(f"No se pudo leer el correo encontrado con ID {mail_id.decode()}")
                return False, "No se pudo leer el correo encontrado", False

            for response_part in datos:
                if not isinstance(response_part, tuple):
                    continue

                mensaje = email.message_from_bytes(response_part[1])

                from_ = mensaje.get("From")
                subject = mensaje.get("Subject")
                date = mensaje.get("Date")
                
                log.info(f"Procesando correo ID {mail_id.decode()}")
                log.info(f"From: {from_}")
                log.info(f"Date: {date}")
                log.info(f"Subject: {subject}")


                for parte in mensaje.walk():
                    if parte.get_content_disposition() != "attachment":
                        continue

                    nombre_archivo = parte.get_filename()
                    if not nombre_archivo:
                        continue

                    try:
                        nombre_decodificado, encoding = decode_header(nombre_archivo)[0]
                        if isinstance(nombre_decodificado, bytes):
                            nombre_decodificado = nombre_decodificado.decode(
                                encoding or "utf-8", errors="ignore"
                            )

                        ruta_archivo = os.path.join(
                            carpeta_descarga, nombre_decodificado
                        )

                        with open(ruta_archivo, "wb") as f:
                            f.write(parte.get_payload(decode=True))
                        
                        # AGREGAR RUTA Y NOMBRES DE ARCHIVOS A LAS LISTAS
                        ruta_adjuntos_descargados.append(ruta_archivo)
                        nombre_adjuntos_descargados.append(nombre_decodificado)
                        adjuntos = True
                    except (OSError, UnicodeDecodeError) as e:
                        log.error(f"Error guardando archivo: {e}")
                        return False, f"Error guardando archivo: {e}", False
            # Marcar correo como leido
            if adjuntos:
                mail.store(mail_id, '+FLAGS', '\\Seen')
                log.info(f"Correo ID {mail_id.decode()} marcado como LEÍDO")
            # # mover correo a etiqueta si tiene etiqueta de destino
            if etiqueta_correo:
                mover_correo_a_etiqueta(mail=mail,mail_id=mail_id,etiqueta_destino=etiqueta_correo)
                log.info(f"Correo ID {mail_id.decode()} movido a etiqueta {etiqueta_correo}")
            
        except imaplib.IMAP4.error as e:
            return False, f"Error procesando correo: {e}", False

        if ruta_adjuntos_descargados:
            return ruta_adjuntos_descargados, "Achivos descargados correctamente", nombre_adjuntos_descargados
        # mail.logout()
        return False, "No se encontraron adjuntos en los correos", False
    except (imaplib.IMAP4.error, socket.gaierror, ssl.SSLError) as e:
        return False, f"Error de conexión IMAP: {e}", False
    except Exception as e:
        return False, f"Error inesperado: {e}", False
    finally:
        if mail:
            mail.logout()

def mover_correo_a_etiqueta(mail, mail_id, etiqueta_destino: str):
    """
    Mueve un correo a una etiqueta/carpeta IMAP.

    :param mail: conexión IMAP ya autenticada
    :param mail_id: ID del correo
    :param etiqueta_destino: nombre de la etiqueta (ej: 'Procesados')
    """
    etiqueta_destino = f'"{etiqueta_destino}"'
    # copiar correo a la etiqueta destino
    status, _ = mail.copy(mail_id, etiqueta_destino)
    if status != "OK":
        raise Exception(f"No se pudo copiar el correo a la etiqueta '{etiqueta_destino}'")

    # marcar el correo original como eliminado
    mail.store(mail_id, '+FLAGS', '\\Deleted')

    # ejecutar eliminación definitiva
    mail.expunge()