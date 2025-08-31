from typing import List, Optional

from pydantic import BaseModel


class LeaderboardPlayerResponseModelV3(BaseModel):
    card: str
    title: str
    is_banned: bool
    is_anonymized: bool
    puuid: Optional[str] = None
    name: str
    tag: str
    updated_at: str


class LeaderboardDataResponseModelV3(BaseModel):
    updated_at: str
    thresholds: Optional[List[dict]]
    players: Optional[List[LeaderboardPlayerResponseModelV3]]
