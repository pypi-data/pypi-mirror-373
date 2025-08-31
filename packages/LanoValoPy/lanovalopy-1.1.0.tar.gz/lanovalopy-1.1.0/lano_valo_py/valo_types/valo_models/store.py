from pydantic import BaseModel

from ..valo_enums import FeaturedItemsVersion


class GetFeaturedItemsFetchOptionsModel(BaseModel):
    version: FeaturedItemsVersion


class GetStoreOffersFetchOptionsModel(BaseModel):
    version: FeaturedItemsVersion
