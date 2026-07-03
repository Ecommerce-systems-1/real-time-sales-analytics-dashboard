from pydantic import BaseModel, Field


class SaleEvent(BaseModel):
    product_id: str
    product_name: str
    quantity: int = Field(..., ge=1)
    unit_price: float = Field(..., ge=0)
    region: str
    funnel_stage: str
    occurred_at: str
