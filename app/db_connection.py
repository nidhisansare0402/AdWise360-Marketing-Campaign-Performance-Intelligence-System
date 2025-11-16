# app/db_connection.py
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import os

def get_db_connection():
    # better: read from environment variables (set in your system or .env)
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASS", "nidhi@2004")   # replace or set env var
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "adwise360")

    # URL-encode password
    safe_pass = quote_plus(DB_PASS)
    url = f"mysql+pymysql://{DB_USER}:{safe_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(url, pool_pre_ping=True)
    return engine
