from typing import Optional

from pydantic import BaseModel, HttpUrl


class GameGearShopDataResponse(BaseModel):
    cost: int
    category: str
    shopOrderPriority: int
    categoryText: str
    gridPosition: dict
    canBeTrashed: bool
    image: Optional[str] = None
    newImage: Optional[str] = None
    newImage2: Optional[str] = None
    assetPath: str


class GearModelResponse(BaseModel):
    uuid: str
    displayName: str
    description: str
    displayIcon: Optional[HttpUrl]
    assetPath: str
    shopData: Optional[GameGearShopDataResponse]
