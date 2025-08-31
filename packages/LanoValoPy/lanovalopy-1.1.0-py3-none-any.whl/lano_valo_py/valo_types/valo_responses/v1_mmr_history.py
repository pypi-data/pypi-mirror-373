from typing import List, Optional

from pydantic import BaseModel


class ImagesModelResponce(BaseModel):
    small: str
    large: str
    triangle_down: str
    triangle_up: str


class MapModel(BaseModel):
    name: str
    id: str


class MatchDataModel(BaseModel):
    currenttier: int
    currenttier_patched: str
    images: ImagesModelResponce
    match_id: str
    map: MapModel
    season_id: str
    ranking_in_tier: int
    mmr_change_to_last_game: int
    elo: int
    date: str
    date_raw: int


class MMRHistoryByPuuidResponseModelV1(BaseModel):
    status: Optional[int] = None
    name: str
    tag: str
    data: List[MatchDataModel]
