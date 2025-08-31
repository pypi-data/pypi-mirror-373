from typing import Optional

from pydantic import BaseModel, Field

from ..valo_enums import Regions, Maps, Modes


class GetStoredMatchesFilterModel(BaseModel):
    page: Optional[int] = Field(1, ge=1)
    size: Optional[int] = Field(20, ge=1, le=100)


class GetStoredMatchesOptionsModel(BaseModel):
    region: Regions
    name: str
    tag: str
    mode: Optional[Modes] = None
    map: Optional[Maps] = None
    filter: GetStoredMatchesFilterModel = Field(
        default_factory=lambda: GetStoredMatchesFilterModel()
    )


class GetStoredMatchesByPUUIDResponseModel(BaseModel):
    puuid: str
    region: Regions
    mode: Optional[Modes] = None
    map: Optional[Maps] = None
    filter: GetStoredMatchesFilterModel = Field(
        default_factory=lambda: GetStoredMatchesFilterModel()
    )
