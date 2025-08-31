from typing import Optional

from pydantic import BaseModel, Field

from ..valo_enums import MMRVersions, Regions, Patforms


class GetMMRStoredHistoryFilterModel(BaseModel):
    page: Optional[int] = Field(None, ge=1)
    size: Optional[int] = Field(None, ge=1, le=20)


class GetMMRStoredHistoryOptionsModel(BaseModel):
    version: MMRVersions
    region: Regions
    name: str
    tag: str
    platform: Optional[Patforms] = None
    filter: Optional[GetMMRStoredHistoryFilterModel] = None


class GetMMRStoredHistoryByPUUIDResponseModel(BaseModel):
    puuid: str
    version: MMRVersions
    region: Regions
    platform: Optional[Patforms] = None
    filter: Optional[GetMMRStoredHistoryFilterModel] = None
