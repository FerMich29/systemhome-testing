import os
import datetime as dt
import uuid
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from db import get_conn

OUT_DIR = os.path.join(os.path.dirname(__file__), "reports_out")
os.makedirs(OUT_DIR, exist_ok=True)

def _query_df(sql: str, params: tuple):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return pd.DataFrame(rows)
    finally:
        conn.close()

def _write_csv(df: pd.DataFrame, filename: str) -> str:
    path = os.path.join(OUT_DIR, filename)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path

def build_daily_report(start_dt: str, end_dt: str) -> dict:
    # Consulta adaptada a tu nueva tabla 'venta'
    sql_sales = """
    SELECT 
        id AS venta_id,
        usuario_id,
        estatus,
        total,
        created_at AS fecha
    FROM venta 
    WHERE created_at >= %s AND created_at < %s
    AND UPPER(estatus) IN ('PAGADA', 'CERRADA')
    ORDER BY created_at;
    """
    
    sql_cancel = """
    SELECT 
        id AS venta_id,
        usuario_id,
        estatus,
        total,
        created_at AS fecha
    FROM venta 
    WHERE created_at >= %s AND created_at < %s
    AND UPPER(estatus) = 'CANCELADA'
    ORDER BY created_at;
    """

    with ThreadPoolExecutor(max_workers=2) as ex:
        f1 = ex.submit(_query_df, sql_sales, (start_dt, end_dt))
        f2 = ex.submit(_query_df, sql_cancel, (start_dt, end_dt))
        df_sales = f1.result()
        df_cancel = f2.result()

    stamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    uid = uuid.uuid4().hex[:10]

    out_sales = _write_csv(df_sales, f"ventas_pagadas_{stamp}_{uid}.csv")
    out_cancel = _write_csv(df_cancel, f"ventas_canceladas_{stamp}_{uid}.csv")

    return {
        "sales_rows": int(len(df_sales)),
        "cancel_rows": int(len(df_cancel)),
        "sales_file": out_sales,
        "cancel_file": out_cancel,
        "range": {"start": start_dt, "end": end_dt}
    }

def build_monthly_report(year: int, month: int) -> dict:
    start = dt.datetime(year, month, 1, 0, 0, 0)
    if month == 12:
        end = dt.datetime(year + 1, 1, 1, 0, 0, 0)
    else:
        end = dt.datetime(year, month + 1, 1, 0, 0, 0)

    return build_daily_report(start.strftime('%Y-%m-%d %H:%M:%S'), end.strftime('%Y-%m-%d %H:%M:%S'))