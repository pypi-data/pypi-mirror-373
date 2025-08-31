from typing import List, Optional
from pydantic import BaseModel


class AccountMmrModelV3(BaseModel):
    puuid: str
    name: str
    tag: str


class SeasonMmrModelV3(BaseModel):
    id: str
    short: str


class TierMmrModelV3(BaseModel):
    id: int
    name: str


class LeaderboardPlacement(BaseModel):
    rank: int
    updated_at: str


class CurrentMmrModelV3(BaseModel):
    tier: Optional[TierMmrModelV3]
    rr: int
    last_change: int
    elo: int
    games_needed_for_rating: int
    rank_protection_shields: int
    leaderboard_placement: Optional[LeaderboardPlacement]


class SeasonalMmrModelV3(BaseModel):
    season: Optional[SeasonMmrModelV3]
    wins: int
    games: int
    end_tier: Optional[TierMmrModelV3]
    end_rr: int
    ranking_schema: str
    leaderboard_placement: Optional[LeaderboardPlacement]
    act_wins: List[TierMmrModelV3]


class PeakMmrModelV3(BaseModel):
    season: SeasonMmrModelV3
    rr: int
    ranking_schema: str
    tier: TierMmrModelV3

class MmrModelV3(BaseModel):
    account: AccountMmrModelV3
    peak: PeakMmrModelV3
    current: CurrentMmrModelV3
    seasonal: List[SeasonalMmrModelV3]