from sqlalchemy import text
from app.db.session import engine

def main():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();")).fetchone()
        print("Connected! Postgres version:", result[0])

if __name__ == "__main__":
    main()
