from typing import List, Optional

from pydantic import BaseModel


class EsportRecordModel(BaseModel):
    wins: int
    losses: int


class EsportTeamModel(BaseModel):
    name: str
    code: str
    icon: Optional[str]
    has_won: bool
    game_wins: int
    record: EsportRecordModel


class EsportGameTypeModel(BaseModel):
    type: str
    count: int


class EsportMatchModel(BaseModel):
    id: str
    game_type: EsportGameTypeModel
    teams: List[EsportTeamModel]


class EsportTournamentModel(BaseModel):
    name: str
    season: str


class EsportLeagueModel(BaseModel):
    name: str
    identifier: str
    icon: Optional[str]
    region: str


class EsportMatchDataResponseModel(BaseModel):
    date: str
    state: str
    type: str
    vod: Optional[str]
    league: EsportLeagueModel
    tournament: EsportTournamentModel
    match: EsportMatchModel
