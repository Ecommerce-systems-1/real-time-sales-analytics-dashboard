import pytest, time
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def setup(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    import app.database as db_mod
    db_mod.DB_PATH = str(tmp_path / "test.db")
    db_mod.init_db()

@pytest.fixture
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c

def test_summary_endpoint_returns_snapshot(client):
    r = client.get("/api/analytics/summary")
    assert r.status_code == 200
    data = r.json()
    assert "total_events" in data
    assert "funnel" in data
    assert "top_products" in data
    assert "sales_by_region" in data
    assert "revenue_by_hour" in data

def test_summary_updates_after_events(client):
    r1 = client.get("/api/analytics/summary")
    t0 = r1.json()["total_events"]
    time.sleep(1.5)  # let generator fire 2–3 events
    r2 = client.get("/api/analytics/summary")
    t1 = r2.json()["total_events"]
    assert t1 > t0

def test_recent_events_endpoint(client):
    time.sleep(0.6)
    r = client.get("/api/analytics/events")
    assert r.status_code == 200
    events = r.json()
    assert isinstance(events, list)
    if events:
        assert "product_id" in events[0]
        assert "funnel_stage" in events[0]

def test_funnel_keys_present(client):
    r = client.get("/api/analytics/summary")
    funnel = r.json()["funnel"]
    assert set(funnel.keys()) == {"VIEWED", "CARTED", "PURCHASED"}

def test_websocket_sends_snapshot(client):
    with client.websocket_connect("/ws/stream") as ws:
        time.sleep(0.7)
        data = ws.receive_json()
        assert "total_events" in data
        assert "funnel" in data