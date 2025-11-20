from sqlalchemy import create_engine
from urllib.parse import quote_plus
import os

def get_db_connection():
    """
    Returns a SQLAlchemy engine connected to the MySQL DB.
    Read credentials from environment variables if present, otherwise use defaults.
    """
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASS", "nidhi@2004")   # replace with your password or set env var
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "adwise360")

    # URL-encode password so special characters don't break the URL
    safe_pass = quote_plus(DB_PASS)
    url = f"mysql+pymysql://{DB_USER}:{safe_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    # pool_pre_ping helps recover from transient disconnects in long-running apps
    engine = create_engine(url, pool_pre_ping=True)
    return engine

