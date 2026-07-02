import uuid
import aiosqlite
from typing import List, Dict, Any

class Database:
    def __init__(self, path: str = '/data/16_real_time_sales_analytics_dashboard.db'):
        self.path = path
        self._conn = None

    async def init(self):
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute('PRAGMA journal_mode=WAL')
        await self._conn.executescript('''
            CREATE TABLE IF NOT EXISTS sales_events (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id TEXT NOT NULL, product_name TEXT NOT NULL, quantity INTEGER NOT NULL, revenue REAL NOT NULL, event_type TEXT NOT NULL, created_at TEXT DEFAULT (datetime('now')));
            CREATE TABLE IF NOT EXISTS metrics_summary (id INTEGER PRIMARY KEY AUTOINCREMENT, metric_key TEXT NOT NULL, metric_value REAL NOT NULL, period TEXT NOT NULL, recorded_at TEXT DEFAULT (datetime('now')));
        ''')
        await self._conn.commit()

    async def close(self):
        if self._conn:
            await self._conn.close()
