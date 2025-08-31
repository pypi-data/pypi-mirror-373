# --- Metadata models ---
from typing import List, Optional

from pydantic import BaseModel


class MatchOSModel(BaseModel):
    name: str
    version: str


class MatchPlatformModel(BaseModel):
    type: str
    os: MatchOSModel


class MatchSessionPlaytimeModel(BaseModel):
    minutes: int
    seconds: int
    milliseconds: int


class MatchAssetsCardModel(BaseModel):
    small: str
    large: str
    wide: str


class MatchAssetsAgentModel(BaseModel):
    small: str
    full: str
    bust: str
    killfeed: str


class MatchAssetsModel(BaseModel):
    card: MatchAssetsCardModel
    agent: MatchAssetsAgentModel


class MatchFriendlyFireModel(BaseModel):
    incoming: int
    outgoing: int


class MatchBehaviourModel(BaseModel):
    afk_rounds: int
    friendly_fire: MatchFriendlyFireModel
    rounds_in_spawn: int


class MatchAbilityCastsModel(BaseModel):
    c_cast: Optional[int] = None
    q_cast: Optional[int] = None
    e_cast: Optional[int] = None
    x_cast: Optional[int] = None


class MatchStatsModel(BaseModel):
    score: int
    kills: int
    deaths: int
    assists: int
    bodyshots: int
    headshots: int
    legshots: int


class MatchEconomySpentModel(BaseModel):
    overall: float | int
    average: float | int


class MatchEconomyLoadoutValueModel(BaseModel):
    overall: float | int
    average: float | int


class MatchEconomyModel(BaseModel):
    spent: MatchEconomySpentModel | int
    loadout_value: MatchEconomyLoadoutValueModel | int


class MatchPlayerModel(BaseModel):
    puuid: Optional[str] = None
    name: str
    tag: str
    team: str
    level: int
    character: str
    currenttier: int
    currenttier_patched: str
    player_card: str
    player_title: str
    party_id: str
    session_playtime: MatchSessionPlaytimeModel
    assets: MatchAssetsModel
    behaviour: Optional[MatchBehaviourModel] = None
    platform: MatchPlatformModel
    ability_casts: MatchAbilityCastsModel
    stats: MatchStatsModel
    economy: MatchEconomyModel
    damage_made: int
    damage_received: int


# --- Team Models ---
class MatchTeamModel(BaseModel):
    has_won: bool
    rounds_won: int
    rounds_lost: int


# --- Main Models ---


class MachPremierInfoModel(BaseModel):
    tournament_id: Optional[str]
    matchup_id: Optional[str]


class MatchMetadataModel(BaseModel):
    map: str
    game_version: str
    game_length: int
    game_start: int
    game_start_patched: str
    rounds_played: int
    mode: str
    mode_id: str
    queue: str
    season_id: str
    platform: str
    matchid: str
    premier_info: Optional[MachPremierInfoModel]
    region: str
    cluster: str


class MatchPlayersModel(BaseModel):
    all_players: List[MatchPlayerModel]
    red: List[MatchPlayerModel]
    blue: List[MatchPlayerModel]


class MatchObserversModel(BaseModel):
    puuid: str
    name: str
    tag: str
    platform: MatchPlatformModel
    session_playtime: MatchSessionPlaytimeModel
    team: str
    level: int
    player_card: str
    player_title: str
    party_id: str


class MatchCoachesModel(BaseModel):
    puuid: str
    team: str


class MatchTeamsModel(BaseModel):
    red: MatchTeamModel
    blue: MatchTeamModel


class MatchDamageEventsModel(BaseModel):
    damage: int
    headshots: int
    bodyshots: int
    legshots: int
    receiver_puuid: str
    receiver_display_name: str
    receiver_team: str


class MacthKillsVictimDeathLocationModel(BaseModel):
    x: int
    y: int


class MatchDamageWeaponAssetsModel(BaseModel):
    display_icon: Optional[str] = None
    killfeed_icon: Optional[str] = None


class MatchDamageAssistantsModel(BaseModel):
    assistant_puuid: str
    assistant_display_name: str
    assistant_team: str


class MatchDamagePlayerLocationsOnKillLocation(BaseModel):
    x: int
    y: int


class MatchDamagePlayerLocationsOnKill(BaseModel):
    view_radians: float
    player_puuid: str
    player_display_name: str
    player_team: str
    location: MatchDamagePlayerLocationsOnKillLocation


class MatchKillsResponseModel(BaseModel):
    kill_time_in_round: int
    kill_time_in_match: int
    round: Optional[int] = None
    killer_puuid: str
    killer_display_name: str
    killer_team: str
    victim_puuid: str
    victim_display_name: str
    victim_team: str
    victim_death_location: Optional[MacthKillsVictimDeathLocationModel]
    damage_weapon_id: str
    damage_weapon_name: Optional[str] = None
    damage_weapon_assets: MatchDamageWeaponAssetsModel
    secondary_fire_mode: bool
    assistants: Optional[List[MatchDamageAssistantsModel]]
    player_locations_on_kill: Optional[List[MatchDamagePlayerLocationsOnKill]]


class MatchRoundPlayerStatsModel(BaseModel):
    ability_casts: MatchAbilityCastsModel
    player_puuid: str
    player_display_name: str
    player_team: str
    damage_events: List[MatchDamageEventsModel]
    damage: int
    headshots: int
    bodyshots: int
    legshots: int
    kill_events: List[MatchKillsResponseModel]
    kills: int
    score: int
    economy: Optional[MatchEconomyModel]
    was_afk: bool
    was_penalized: bool
    stayed_in_spawn: bool


MatchRoundPlayerLocationOnPlant = MatchDamagePlayerLocationsOnKill


class MatchRoundPlantEventPlantLocationModel(BaseModel):
    x: int
    y: int


class MatchRoundPlantedByModel(BaseModel):
    puuid: str
    display_name: str
    team: str


class MatchRoundPlantEventModel(BaseModel):
    plant_location: Optional[MatchRoundPlantEventPlantLocationModel] = None
    planted_by: Optional[MatchRoundPlantedByModel] = None
    plant_site: Optional[str] = None
    plant_time_in_round: Optional[int] = None
    player_locations_on_plant: Optional[List[MatchRoundPlayerLocationOnPlant]] = None


MatchRoundDefuseEventLocationModel = MatchRoundPlantEventPlantLocationModel
MatchRoundDefuseEventDefusedByModel = MatchRoundPlantedByModel
MatchRoundPlayerLocationOnDefuseModel = MatchRoundPlayerLocationOnPlant


class MatchRoundDefuseEventModel(BaseModel):
    defuse_location: Optional[MatchRoundDefuseEventLocationModel]
    defused_by: Optional[MatchRoundDefuseEventDefusedByModel]
    defuse_time_in_round: Optional[int]
    player_locations_on_defuse: Optional[List[MatchRoundPlayerLocationOnDefuseModel]]


class MatchRoundModel(BaseModel):
    winning_team: str
    end_type: str
    bomb_planted: bool
    bomb_defused: bool
    plant_events: Optional[MatchRoundPlantEventModel]
    defuse_events: Optional[MatchRoundDefuseEventModel]
    player_stats: List[MatchRoundPlayerStatsModel]


class MatchResponseModel(BaseModel):
    metadata: MatchMetadataModel
    players: MatchPlayersModel
    observers: List[MatchObserversModel]
    coaches: List[MatchCoachesModel]
    teams: MatchTeamsModel
    rounds: List[MatchRoundModel]
    kills: List[MatchKillsResponseModel]

    def to_match_data_v4(self): ...


class PlayerStatsModel(BaseModel):
    kill_diff: int
    kd_ratio: float
    avg_kills_per_round: float
    headshot_percent: float
    kast: float
    first_kills: int
    first_deaths: int
    multi_kills: int
    avg_damage_per_round: float


class TotalPlayerStatsModel(BaseModel):
    stats: PlayerStatsModel | None = None
    duels: dict[str, int] | None = None
