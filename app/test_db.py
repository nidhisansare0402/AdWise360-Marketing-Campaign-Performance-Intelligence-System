# app/test_db.py
from db_connection import get_db_connection
from sqlalchemy import text

engine = get_db_connection()

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("DB connected, test query result:", result.scalar())
except Exception as e:
    print("DB connection failed:", repr(e))
