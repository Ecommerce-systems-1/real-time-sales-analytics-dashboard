import pytest
from app.aggregator import AggState
from app.models import SaleEvent
from datetime import datetime, timezone

def make_event(product_id="PROD-001", product_name="Widget", qty=2,
               price=10.0, region="NORTH", stage="PURCHASED", ts=None):
    return SaleEvent(
        product_id=product_id,
        product_name=product_name,
        quantity=qty,
        unit_price=price,
        region=region,
        funnel_stage=stage,
        occurred_at=ts or datetime.now(timezone.utc).isoformat()
    )

def test_initial_state_empty():
    s = AggState()
    snap = s.snapshot()
    assert snap["total_events"] == 0
    assert snap["funnel"] == {"VIEWED": 0, "CARTED": 0, "PURCHASED": 0}

def test_update_increments_total():
    s = AggState()
    s.update(make_event())
    assert s.snapshot()["total_events"] == 1

def test_revenue_only_counts_purchased():
    s = AggState()
    s.update(make_event(qty=2, price=10.0, stage="PURCHASED"))
    s.update(make_event(qty=1, price=10.0, stage="VIEWED"))  # should NOT add revenue
    snap = s.snapshot()
    total_revenue = sum(snap["revenue_by_hour"].values())
    assert total_revenue == 20.0  # only PURCHASED contributes

def test_top_products_ranked_by_revenue():
    s = AggState()
    s.update(make_event("PROD-A", "Alpha", 1, 100.0, stage="PURCHASED"))
    s.update(make_event("PROD-B", "Beta",  5, 10.0,  stage="PURCHASED"))
    snap = s.snapshot()
    products = snap["top_products"]
    assert products[0]["product_id"] == "PROD-A"  # 100 > 50
    assert products[0]["revenue"] == 100.0

def test_region_sales_aggregation():
    s = AggState()
    s.update(make_event(region="NORTH", qty=2, price=15.0, stage="PURCHASED"))
    s.update(make_event(region="SOUTH", qty=1, price=25.0, stage="PURCHASED"))
    snap = s.snapshot()
    assert snap["sales_by_region"]["NORTH"] == 30.0
    assert snap["sales_by_region"]["SOUTH"] == 25.0

def test_funnel_counts_all_stages():
    s = AggState()
    s.update(make_event(stage="VIEWED"))
    s.update(make_event(stage="VIEWED"))
    s.update(make_event(stage="CARTED"))
    s.update(make_event(stage="PURCHASED"))
    snap = s.snapshot()
    assert snap["funnel"]["VIEWED"] == 2
    assert snap["funnel"]["CARTED"] == 1
    assert snap["funnel"]["PURCHASED"] == 1

def test_revenue_by_hour_bucket():
    s = AggState()
    # Same hour = same bucket
    ts = "2025-06-01T14:30:00"
    s.update(make_event(qty=1, price=50.0, stage="PURCHASED", ts=ts))
    s.update(make_event(qty=1, price=30.0, stage="PURCHASED", ts=ts))
    snap = s.snapshot()
    hour_bucket = "2025-06-01T14"
    assert snap["revenue_by_hour"].get(hour_bucket) == 80.0

def test_top_products_limited_to_10():
    s = AggState()
    for i in range(15):
        s.update(make_event(f"PROD-{i:03d}", f"Product {i}", 1, float(i), stage="PURCHASED"))
    snap = s.snapshot()
    assert len(snap["top_products"]) <= 10

def test_rebuild_from_events():
    s = AggState()
    events = [make_event(qty=1, price=25.0, stage="PURCHASED") for _ in range(5)]
    s.rebuild(events)
    snap = s.snapshot()
    assert snap["total_events"] == 5
    total_rev = sum(snap["revenue_by_hour"].values())
    assert total_rev == 125.0