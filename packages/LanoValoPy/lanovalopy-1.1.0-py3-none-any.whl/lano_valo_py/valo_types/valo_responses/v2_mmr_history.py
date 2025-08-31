from typing import List

from pydantic import BaseModel


class AccountMMRHistoryV2(BaseModel):
    puuid: str
    name: str
    tag: str


class SeasonMMRHistoryModelV2(BaseModel):
    id: str
    short: str


class TierMMRHistoryModelV2(BaseModel):
    id: int
    name: str


class MapMMRHistoryModelV2(BaseModel):
    id: str
    name: str


class HistoryMMRV2(BaseModel):
    match_id: str
    rr: int
    last_change: int
    elo: int
    refunded_rr: int
    was_derank_protected: bool
    date: str
    map: MapMMRHistoryModelV2
    tier: TierMMRHistoryModelV2
    season: SeasonMMRHistoryModelV2


class MMRHistoryModelV2(BaseModel):
    account: AccountMMRHistoryV2
    history: List[HistoryMMRV2]
