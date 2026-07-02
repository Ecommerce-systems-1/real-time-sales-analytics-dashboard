import asyncio, pytest
from app.generator import make_random_event
from app.models import SaleEvent

def test_make_random_event_returns_sale_event():
    e = make_random_event()
    assert isinstance(e, SaleEvent)
    assert e.funnel_stage in {"VIEWED", "CARTED", "PURCHASED"}
    assert e.region in {"NORTH", "SOUTH", "EAST", "WEST"}
    assert 1 <= e.quantity <= 5
    assert e.unit_price > 0

def test_make_random_event_valid_product():
    e = make_random_event()
    assert e.product_id.startswith("PROD-")
    assert len(e.product_name) > 0

def test_events_are_random_not_identical():
    events = [make_random_event() for _ in range(20)]
    regions = {e.region for e in events}
    assert len(regions) > 1  # not all same region (astronomically unlikely)