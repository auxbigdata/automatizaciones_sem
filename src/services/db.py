import psycopg2
from psycopg2.extras import RealDictCursor
from src.settings.entorno import env

def get_connection():
    return psycopg2.connect(
        host=env.DB_HOST,
        port=env.DB_PORT,
        dbname=env.DB_NAME,
        user=env.DB_USER,
        password=env.DB_PASS
    )

def ejecutar_query(sql, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            if cur.description:
                return cur.fetchall()
            conn.commit()
            return None
    finally:
        conn.close()

def ejecutar_query_dict(sql, params=None):
    """
    Igual que ejecutar_query, pero devuelve cada fila como diccionario
    (nombre de columna -> valor) en vez de tupla. Se usa en robots donde
    conviene acceder a las columnas por nombre (ej. registro.get("id")),
    sin afectar a los robots que ya dependen de ejecutar_query devolviendo tuplas.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params or ())
            if cur.description:
                return [dict(fila) for fila in cur.fetchall()]
            conn.commit()
            return None
    finally:
        conn.close()