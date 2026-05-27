import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="papershield",
        user="postgres",
        password="password"
    )

def setup_database():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contract_chunks (
            id SERIAL PRIMARY KEY,
            document_id TEXT NOT NULL,
            chunk_text TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            embedding vector(1536)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Database ready.")

if __name__ == "__main__":
    setup_database()