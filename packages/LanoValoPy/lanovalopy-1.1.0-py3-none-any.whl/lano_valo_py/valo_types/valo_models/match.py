from typing import Optional

from pydantic import BaseModel

from ..valo_enums import (
    Maps,
    Modes,
    Regions,
    MatchListVersion
)


class GetMatchesByPUUIDFetchOptionsModel(BaseModel):
    region: Regions
    puuid: str
    version: MatchListVersion
    filter: Optional[Modes] = None
    map: Optional[Maps] = None
    size: Optional[int] = None


class GetMatchesFetchOptionsModel(BaseModel):
    region: Regions
    name: str
    tag: str
    version: MatchListVersion
    filter: Optional[Modes] = None
    map: Optional[Maps] = None
    size: Optional[int] = None


class GetMatchFetchOptionsModel(BaseModel):
    match_id: str
    region: Optional[Regions]
    version: MatchListVersion