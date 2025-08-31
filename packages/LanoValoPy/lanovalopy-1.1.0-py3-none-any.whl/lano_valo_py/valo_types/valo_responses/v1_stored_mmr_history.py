from pydantic import BaseModel


class V1StoredMmrHistoryTier(BaseModel):
    id: int
    name: str


class V1StoredMmrHistoryMap(BaseModel):
    id: str
    name: str


class V1StoredMmrHistorySeason(BaseModel):
    id: str
    short: str


class V1StoredMmrHistoryResponse(BaseModel):
    match_id: str
    map: V1StoredMmrHistoryMap
    tier: V1StoredMmrHistoryTier
    season: V1StoredMmrHistorySeason
    ranking_in_tier: int
    last_mmr_change: int
    elo: int
    date: str