import asyncio, json, logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self._clients: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self._clients.add(ws)
        logger.info(f"WS connected. Total clients: {len(self._clients)}")

    async def disconnect(self, ws: WebSocket):
        async with self._lock:
            self._clients.discard(ws)
        logger.info(f"WS disconnected. Total clients: {len(self._clients)}")

    async def broadcast(self, snapshot: dict):
        msg = json.dumps(snapshot)
        dead = set()
        async with self._lock:
            clients = set(self._clients)
        for ws in clients:
            try:
                await ws.send_text(msg)
            except Exception:
                dead.add(ws)
        if dead:
            async with self._lock:
                self._clients -= dead

manager = ConnectionManager()