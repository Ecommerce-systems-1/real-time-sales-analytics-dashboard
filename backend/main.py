import asyncio, os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database import init_db, write_event, replay_events
from app.aggregator import AggState
from app.generator import generate_events
from app.broadcaster import manager
from app.models import SaleEvent

agg = AggState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    past_events = replay_events()
    agg.rebuild(past_events)
    task = asyncio.create_task(
        generate_events(agg, write_event, manager.broadcast, interval=0.5)
    )
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(title="Real-Time Sales Analytics", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.websocket("/ws/stream")
async def ws_stream(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json(agg.snapshot())
        while True:
            await websocket.receive_text()  # keep alive; browser may send pings
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        await manager.disconnect(websocket)

@app.get("/api/analytics/summary")
def get_summary():
    return JSONResponse(agg.snapshot())

@app.get("/api/analytics/events")
def get_recent_events():
    from app.database import get_recent_raw_events
    return get_recent_raw_events(100)

static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "out")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")