from typing import Optional

from pydantic import BaseModel

from ..valo_enums import LeaderboardEpisodes, LeaderboardVersions, Regions


class GetLeaderboardOptionsModel(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None
    version: LeaderboardVersions
    region: Regions
    name: Optional[str] = None
    tag: Optional[str] = None
    puuid: Optional[str] = None
    season: Optional[LeaderboardEpisodes] = None
