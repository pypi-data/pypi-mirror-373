from typing import Optional, List

from pydantic import BaseModel


class BundleResponseItemModelV2(BaseModel):
    uuid: str
    name: str
    image: Optional[str]
    type: str
    amount: int
    discount_percent: float
    base_price: float
    discounted_price: float
    promo_item: bool


class BundleResponseModelV2(BaseModel):
    bundle_uuid: str
    seconds_remaining: int
    bundle_price: int
    whole_sale_only: bool
    expires_at: str
    items: List[BundleResponseItemModelV2]