import paramiko

def conexion_sh(ip, puerto, username, password, log):
    # host = ip
    # port = 22
    # username = 'gamble'
    # password = 'consuerte'

    host = ip
    port = puerto
    username = username
    password = password

    try:
        # print("Iniciando Conexion SH")
        log.info("Iniciando Conexion SH")
        log.info(f"Host: {host}, Puerto: {port}, username: {username}, password: {password}")
        # Crea un cliente SSH
        client = paramiko.SSHClient()
        # Configura el cliente para que no solicite confirmación de clave pública
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Conecta al servidor
        client.connect(host, port, username, password)
        log.info(f"Se conecto al servidor: {host}")
        return client
    except paramiko.AuthenticationException:
        log.error("Error de autenticación: usuario o contraseña incorrectos")
        return False
    except paramiko.SSHException as e:
        log.error(f"Error en la conexion SSH: {e}")
        return False
    except Exception as e:
        log.error(f"Error inesperado: {e}")
        return False
    
def comandos_ssh(log, comandos, client):
    log.info(f"Ejecutando comando: {comandos}")

    try:
        for cmd in comandos:
            log.info(f"Ejecutando comando: {cmd}: {comandos[cmd]}")
            stdin, stdout, stderr = client.exec_command(comandos[cmd])
            salida = stdout.read().decode()
            errores = stderr.read().decode()

            log.info(f"Salida: {salida}")
            log.error(f"Errores: {errores}")


    except Exception as e:
        log.error(f"Error ejecutando comandos: {e}")