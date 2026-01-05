import duckdb
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "db" / "steam.duckdb"

def get_connection():
    return duckdb.connect(DB_PATH)

def init_tables():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_concurrency (
            appid INTEGER,
            game_name VARCHAR,
            concurrent_players INTEGER,
            collected_at TIMESTAMP
        )
    """)
    conn.close()
