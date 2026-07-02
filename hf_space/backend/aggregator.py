import threading
from collections import defaultdict
from datetime import datetime, timezone
from app.models import SaleEvent

class AggState:
    def __init__(self):
        self._lock = threading.Lock()
        self._revenue_by_hour: dict = defaultdict(float)
        self._products: dict = {}     # product_id → {name, count, revenue}
        self._region_sales: dict = defaultdict(float)
        self._funnel: dict = defaultdict(int)
        self._total = 0

    def update(self, event: SaleEvent) -> None:
        with self._lock:
            self._total += 1
            self._funnel[event.funnel_stage] += 1
            if event.funnel_stage == "PURCHASED":
                revenue = event.unit_price * event.quantity
                hour_bucket = event.occurred_at[:13]  # "YYYY-MM-DDTHH"
                self._revenue_by_hour[hour_bucket] += revenue
                self._region_sales[event.region] += revenue
                if event.product_id not in self._products:
                    self._products[event.product_id] = {"product_id": event.product_id,
                                                         "name": event.product_name,
                                                         "count": 0, "revenue": 0.0}
                self._products[event.product_id]["count"] += event.quantity
                self._products[event.product_id]["revenue"] += revenue

    def rebuild(self, events: list) -> None:
        for e in events:
            self.update(e)

    def snapshot(self) -> dict:
        with self._lock:
            sorted_products = sorted(
                self._products.values(), key=lambda p: p["revenue"], reverse=True
            )[:10]
            return {
                "total_events": self._total,
                "revenue_by_hour": dict(self._revenue_by_hour),
                "top_products": sorted_products,
                "sales_by_region": dict(self._region_sales),
                "funnel": {
                    "VIEWED": self._funnel.get("VIEWED", 0),
                    "CARTED": self._funnel.get("CARTED", 0),
                    "PURCHASED": self._funnel.get("PURCHASED", 0),
                },
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }