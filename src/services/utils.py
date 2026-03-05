from datetime import datetime, timedelta

def obtener_fecha_ayer():
    ayer = datetime.now() - timedelta(days=1)
    return ayer.strftime("%Y/%m/%d")