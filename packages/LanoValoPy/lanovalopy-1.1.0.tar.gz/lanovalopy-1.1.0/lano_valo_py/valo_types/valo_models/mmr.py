from typing import Optional

from pydantic import BaseModel

from ..valo_enums import (
    Episodes,
    MMRHistoryVersions,
    MMRVersions,
    Regions,
)


class GetMMRByPUUIDFetchOptionsModel(BaseModel):
    version: MMRVersions
    region: Regions
    puuid: str
    filter: Optional[Episodes] = None


class GetMMRHistoryByPUUIDFetchOptionsModel(BaseModel):
    region: Regions
    puuid: str
    version: MMRHistoryVersions



class GetLifetimeMMRHistoryFetchOptionsModel(BaseModel):
    region: Regions
    name: str
    tag: str
    page: Optional[int] = None
    size: Optional[int] = None


class GetMMRFetchOptionsModel(BaseModel):
    version: MMRVersions
    region: Regions
    name: str
    tag: str
    filter: Optional[Episodes] = None


class GetMMRHistoryFetchOptionsModel(BaseModel):
    name: str
    tag: str
    region: Regions
    version: MMRHistoryVersions
