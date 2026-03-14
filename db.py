import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""), # Generalmente vacío en XAMPP
        database="checador", # <--- Cambiado de 'biblioteca' a 'ventas'
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )