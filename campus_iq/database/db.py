"""SQLite connection, transactions and lightweight data migrations."""
import sqlite3
from contextlib import contextmanager
from config import DB_PATH, DATA_DIR
def get_connection():
    DATA_DIR.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(DB_PATH); conn.row_factory=sqlite3.Row; conn.execute("PRAGMA foreign_keys = ON")
    return conn
@contextmanager
def connection():
    conn=get_connection()
    try: yield conn; conn.commit()
    except Exception: conn.rollback(); raise
    finally: conn.close()
def initialize_database():
    from database.schema import SCHEMA
    with connection() as conn: conn.executescript(SCHEMA)
    from database.seed import seed_database
    seed_database()
    # Keep clearly-labelled demonstration meter readings visible in the current month.
    with connection() as conn:
        conn.execute("UPDATE energy_records SET recorded_on=date('now','start of month') WHERE source='Demo' AND recorded_on='2026-10-01'")
