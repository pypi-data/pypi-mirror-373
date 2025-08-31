from typing import List, Optional

from pydantic import BaseModel


class LeaderboardPlayerResponseModelV2(BaseModel):
    PlayerCardID: str
    TitleID: str
    IsBanned: bool
    IsAnonymized: bool
    puuid: Optional[str] = None
    gameName: str
    tagLine: str
    leaderboardRank: int
    rankedRating: int
    numberOfWins: int
    competitiveTier: int


class LeaderboardDataResponseModelV2(BaseModel):
    last_update: int
    next_update: int
    total_players: int
    radiant_threshold: int
    immortal_3_threshold: int
    immortal_2_threshold: int
    immortal_1_threshold: int
    players: List[LeaderboardPlayerResponseModelV2]