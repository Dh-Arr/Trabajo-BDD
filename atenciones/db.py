"""Conexión a PostgreSQL y funciones auxiliares."""
import os
from contextlib import closing

import pandas as pd
import psycopg2


def get_conn():
    # Ajusta estos valores (o define variables de entorno PG*)
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "atenciones"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "postgres"),
    )


def consultar(sql, params=None):
    """Ejecuta un SELECT y devuelve un DataFrame."""
    with closing(get_conn()) as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        columnas = [d[0] for d in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=columnas)


def ejecutar(sql, params=None):
    """Ejecuta INSERT/UPDATE (con commit). Lanza psycopg2.Error si falla."""
    with closing(get_conn()) as conn:
        with conn, conn.cursor() as cur:  # 'with conn' hace commit/rollback
            cur.execute(sql, params)
