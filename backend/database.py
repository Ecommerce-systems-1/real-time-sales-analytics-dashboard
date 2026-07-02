import sqlite3, os
from contextlib import contextmanager
from app.models import SaleEvent
from datetime import datetime, timezone

DB_PATH = os.environ.get("DB_PATH", "analytics.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

@contextmanager
def db_session():
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with db_session() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS sale_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL, product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL, unit_price REAL NOT NULL,
            region TEXT NOT NULL, funnel_stage TEXT NOT NULL,
            occurred_at TEXT NOT NULL
        )""")

def write_event(event: SaleEvent):
    with db_session() as conn:
        conn.execute(
            "INSERT INTO sale_events(product_id,product_name,quantity,unit_price,region,funnel_stage,occurred_at) VALUES (?,?,?,?,?,?,?)",
            (event.product_id, event.product_name, event.quantity, event.unit_price,
             event.region, event.funnel_stage, event.occurred_at)
        )

def replay_events() -> list:
    with db_session() as conn:
        rows = conn.execute("SELECT * FROM sale_events ORDER BY id").fetchall()
    return [SaleEvent(**dict(r)) for r in rows]

def get_recent_raw_events(limit: int) -> list:
    with db_session() as conn:
        rows = conn.execute(
            "SELECT * FROM sale_events ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]