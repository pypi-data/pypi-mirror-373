from typing import List

from pydantic import BaseModel


class ItemResponseModel(BaseModel):
    ItemTypeID: str
    ItemID: str
    Amount: int


class BundleItemResponseModel(BaseModel):
    Item: ItemResponseModel
    BasePrice: float
    CurrencyID: str
    DiscountPercent: float
    DiscountedPrice: float
    IsPromoItem: bool


class BundleResponseModel(BaseModel):
    ID: str
    DataAssetID: str
    CurrencyID: str
    Items: List[BundleItemResponseModel]
    DurationRemainingInSeconds: int


class FeaturedBundleModel(BaseModel):
    Bundle: BundleResponseModel
    Bundles: List[BundleResponseModel]
    BundleRemainingDurationInSeconds: int


class FeaturedBundleResponseModelV1(BaseModel):
    FeaturedBundle: FeaturedBundleModel