from db_connection import get_db_connection
from sqlalchemy import text

def test_conn():
    engine = get_db_connection()
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("DB test OK:", result.scalar())
    except Exception as e:
        print("DB test FAILED:", e)

if __name__ == "__main__":
    test_conn()
