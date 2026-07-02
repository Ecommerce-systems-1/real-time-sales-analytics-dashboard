import asyncio, random, logging
from datetime import datetime, timezone
from app.models import SaleEvent

logger = logging.getLogger(__name__)

PRODUCTS = [
    ("PROD-001","Running Shoes"),("PROD-002","Backpack"),("PROD-003","Water Bottle"),
    ("PROD-004","Yoga Mat"),("PROD-005","Headphones"),("PROD-006","T-Shirt"),
    ("PROD-007","Jeans"),("PROD-008","Sunglasses"),("PROD-009","Watch"),("PROD-010","Sneakers"),
    ("PROD-011","Jacket"),("PROD-012","Hat"),("PROD-013","Belt"),("PROD-014","Wallet"),
    ("PROD-015","Socks"),("PROD-016","Gloves"),("PROD-017","Scarf"),("PROD-018","Boots"),
    ("PROD-019","Dress"),("PROD-020","Shorts"),
]
PRICES = {pid: round(random.uniform(9.99, 199.99), 2) for pid, _ in PRODUCTS}
REGIONS = ["NORTH", "SOUTH", "EAST", "WEST"]
STAGES = ["VIEWED", "VIEWED", "VIEWED", "CARTED", "CARTED", "PURCHASED"]  # weighted

def make_random_event() -> SaleEvent:
    pid, pname = random.choice(PRODUCTS)
    return SaleEvent(
        product_id=pid,
        product_name=pname,
        quantity=random.randint(1, 5),
        unit_price=PRICES[pid],
        region=random.choice(REGIONS),
        funnel_stage=random.choice(STAGES),
        occurred_at=datetime.now(timezone.utc).isoformat(),
    )

async def generate_events(agg_state, db_write_fn, notify_fn, interval: float = 0.5):
    while True:
        try:
            event = make_random_event()
            agg_state.update(event)
            try:
                db_write_fn(event)
            except Exception as e:
                logger.warning(f"DB write failed: {e}")
            await notify_fn(agg_state.snapshot())
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Generator error: {e}")
            await asyncio.sleep(1.0)