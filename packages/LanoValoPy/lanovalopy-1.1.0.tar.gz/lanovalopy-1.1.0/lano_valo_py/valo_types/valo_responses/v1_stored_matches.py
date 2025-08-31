from pydantic import BaseModel


class StoredMatchTeamResponseModel(BaseModel):
    red: int
    blue: int


class StoredMatchStatsCharacterResponseModel(BaseModel):
    id: str
    name: str

class StoredMatchStatsShotsResponseModel(BaseModel):
    head: int 
    body: int
    leg: int

class StoredMatchStatsDamageResponseModel(BaseModel):
    made: int
    received: int

class StoredMatchStatsResponseModel(BaseModel):
    puuid: str
    team: str
    level: int
    character: StoredMatchStatsCharacterResponseModel
    tier: int
    score: int
    kills: int
    deaths: int
    assists:int
    shots: StoredMatchStatsShotsResponseModel
    damage: StoredMatchStatsDamageResponseModel

class StoredMatchMetaMapResponseModel(BaseModel):
    id: str
    name: str


class StoredMatchMetaSeasonResponseModel(BaseModel):
    id: str
    short: str


class StoredMatchesMetaResponseModel(BaseModel):
    id: str
    map: StoredMatchMetaMapResponseModel
    version: str
    mode: str
    started_at:  str
    season: StoredMatchMetaSeasonResponseModel
    region:  str
    cluster:  str


class StoredMatchResponseModel(BaseModel):
    meta: StoredMatchesMetaResponseModel
    stats: StoredMatchStatsResponseModel
    teams: StoredMatchTeamResponseModel
