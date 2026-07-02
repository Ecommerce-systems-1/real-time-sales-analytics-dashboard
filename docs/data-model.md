# Data Model — Real-Time Sales Analytics Dashboard

```sql
CREATE TABLE IF NOT EXISTS sales_events (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id TEXT NOT NULL, product_name TEXT NOT NULL, quantity INTEGER NOT NULL, revenue REAL NOT NULL, event_type TEXT NOT NULL, created_at TEXT DEFAULT (datetime('now')));
```
