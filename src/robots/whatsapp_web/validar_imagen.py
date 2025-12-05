import os
from datetime import datetime, timedelta

def obtener_nombre_esperado():
    hora_actual = datetime.now()

    # extension = os.path.splitext(archivo)[1].lower()
    # if extension != ".png":
    #     return None  # No es una imagen vÃ¡lida

    # print(f"Imagen detectada: {archivo}")

    # === VALIDACIONES POR HORARIO ===

    # 1. Horario de madrugada: 3:00 a.m.
    if 2 <= hora_actual.hour <= 8:
        fecha = (hora_actual - timedelta(days=1)).strftime("%d-%m-%Y")
        return f"{fecha}.png"

    # 2. Horario de 1:45 p.m. â†’ 13:00 a 13:59
    if 12 <= hora_actual.hour < 15:
        fecha = hora_actual.strftime("%d-%m-%Y")
        return f"130_{fecha}.png"

    # 3. Horario de 4:45 p.m. â†’ 16:00 a 16:59
    if 15 <= hora_actual.hour < 23:
        fecha = hora_actual.strftime("%d-%m-%Y")
        return f"430_{fecha}.png"

    print("No es un horario vÃ¡lido para validar imÃ¡genes.")
    return None

def buscar_imagen():
    nombre_esperado = obtener_nombre_esperado()
    # carpeta = r"python/10.1.1.1/codesarpamoni/Escrutinio"
    carpeta = os.path.dirname(__file__)
    if nombre_esperado is None:
        print("No es un horario vÃ¡lido.")
        return None
    else:
        ruta_archivo = os.path.join(carpeta, nombre_esperado)
        if os.path.exists(ruta_archivo):
            print("âœ” Imagen encontrada:", ruta_archivo)
            return ruta_archivo
        else:
            print("â�Œ Imagen NO encontrada:", ruta_archivo)
            return None

# # archivo = os.path.basename(ruta)
#     hora_actual = datetime.now()
#         extension = os.path.splitext(archivo)[1].lower()

#         # Validamos solo archivos PNG
#         if extension != ".png":
#             return

#         print(f"Imagen detectada: {archivo}")

#         # Obtenemos la fecha de referencia segÃ¯Â¿Â½n la hora
#         if 0 <= hora_actual.hour < 3:
#             # Madrugada (dÃ¯Â¿Â½a anterior)
#             fecha = (hora_actual - timedelta(days=1)).strftime("%d-%m-%Y")
#             nombre_esperado = f"{fecha}.png"
#         elif 0 <= hora_actual.hour < 15:
#             # Entre 12 a.m. y 2 p.m.
#             fecha = hora_actual.strftime("%d-%m-%Y")
#             nombre_esperado = f"130_{fecha}.png"
#         elif 15 <= hora_actual.hour < 17:
#             # Entre 3 p.m. y 5 p.m.
#             fecha = hora_actual.strftime("%d-%m-%Y")
#             nombre_esperado = f"430_{fecha}.png"
#         else:
#             print("No es un horario vÃƒÂ¡lido para validar imÃ¯Â¿Â½genes.")
#             return