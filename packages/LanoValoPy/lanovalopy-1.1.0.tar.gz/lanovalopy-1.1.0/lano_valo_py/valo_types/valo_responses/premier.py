from typing import List

from pydantic import BaseModel


class PremierStats(BaseModel):
    wins: int
    matches: int
    losses: int


class PremierPlacement(BaseModel):
    points: int
    conference: str
    division: int
    place: int


class PremierCustomization(BaseModel):
    icon: str
    image: str
    primary: str
    secondary: str
    tertiary: str


class PremierMember(BaseModel):
    puuid: str
    name: str
    tag: str


class PremierTeamResponseModel(BaseModel):
    id: str
    name: str
    tag: str
    enrolled: bool
    stats: PremierStats
    placement: PremierPlacement
    customization: PremierCustomization
    member: List[PremierMember]


class PremierLeagueMatch(BaseModel):
    id: str
    points_before: int
    points_after: int
    started_at: str


class PremierLeagueMatchesWrapperResponseModel(BaseModel):
    league_matches: List[PremierLeagueMatch]
