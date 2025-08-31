from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

# Nested models first
class Location(BaseModel):
    x: int
    y: int

class PlayerInfo(BaseModel):
    puuid: str
    name: str
    tag: str
    team: Optional[str] = None

class Damage(BaseModel):
    dealt: int
    received: int

class Stats(BaseModel):
    score: int
    kills: int
    deaths: Optional[int] = None
    assists: Optional[int] = None
    headshots: int
    legshots: int
    bodyshots: int
    damage: Optional[Damage] = None

class AbilityCasts(BaseModel):
    grenade: Optional[int] = 0
    ability_1: Optional[int] = 0
    ability_2: Optional[int] = 0
    ultimate: Optional[int] = 0

class Tier(BaseModel):
    id: int
    name: str

class FriendlyFire(BaseModel):
    incoming: int
    outgoing: int

class Behavior(BaseModel):
    afk_rounds: Optional[int | float] = 0
    friendly_fire: FriendlyFire
    rounds_in_spawn: int | float

class EconomySpent(BaseModel):
    overall: int
    average: Optional[int | float] = 0

class Economy(BaseModel):
    spent: EconomySpent
    loadout_value: EconomySpent

class Agent(BaseModel):
    id: str
    name: str

class Player(BaseModel):
    puuid: str
    name: str
    tag: str
    team_id: str
    platform: str
    party_id: str
    agent: Agent
    stats: Stats
    ability_casts: AbilityCasts
    tier: Tier
    card_id: Optional[str] = None
    title_id: Optional[str] = None
    prefered_level_border: Optional[str] = None
    account_level: int
    session_playtime_in_ms: int
    behavior: Optional[Behavior] = None
    economy: Economy

class Observer(BaseModel):
    puuid: str
    name: str
    tag: str
    account_level: int
    session_playtime_in_ms: int
    card_id: str
    title_id: str
    party_id: str

class Coach(BaseModel):
    puuid: str
    team_id: str

class Customization(BaseModel):
    icon: str
    image: str
    primary_color: str
    secondary_color: str
    tertiary_color: str

class PremierRoster(BaseModel):
    id: str
    name: str
    tag: str
    members: List[str]
    customization: Customization

class Rounds(BaseModel):
    won: int
    lost: int

class Team(BaseModel):
    team_id: str
    rounds: Rounds
    won: bool
    premier_roster: Optional[PremierRoster] = None

class PlayerLocation(BaseModel):
    puuid: Optional[str] = None
    name: Optional[str] = None
    tag: Optional[str] = None
    team: Optional[str] = None
    view_radians: float
    location: Location

class Plant(BaseModel):
    round_time_in_ms: int
    site: str
    location: Location
    player: PlayerInfo
    player_locations: List[PlayerLocation]

class Defuse(BaseModel):
    round_time_in_ms: int
    location: Location
    player: PlayerInfo
    player_locations: List[PlayerLocation]

class DamageEvent(BaseModel):
    puuid: Optional[str] = None
    name: Optional[str] = None
    tag: Optional[str] = None
    team: Optional[str] = None
    bodyshots: int
    headshots: int
    legshots: int
    damage: int

class Weapon(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None

class Armor(BaseModel):
    id: str
    name: str

class RoundEconomy(BaseModel):
    loadout_value: int
    remaining: int
    weapon: Optional[Weapon] = None
    armor: Optional[Armor] = None

class RoundStats(BaseModel):
    ability_casts: AbilityCasts
    player: PlayerInfo
    damage_events: List[DamageEvent]
    stats: Stats
    economy: RoundEconomy
    was_afk: bool
    received_penalty: bool
    stayed_in_spawn: bool

class Round(BaseModel):
    id: int
    result: str
    ceremony: str
    winning_team: str
    plant: Optional[Plant] = None
    defuse: Optional[Defuse] = None
    stats: List[RoundStats]

class Kill(BaseModel):
    round: int
    time_in_round_in_ms: int
    time_in_match_in_ms: int
    killer: PlayerInfo
    victim: PlayerInfo
    assistants: List[PlayerInfo]
    location: Location
    weapon: Weapon
    secondary_fire_mode: bool
    player_locations: List[PlayerLocation]

class Map(BaseModel):
    id: str
    name: str

class Queue(BaseModel):
    id: str
    name: str
    mode_type: str

class Season(BaseModel):
    id: str
    short: str

class PartyPenalty(BaseModel):
    party_id: str
    penalty: int

class Metadata(BaseModel):
    match_id: str
    map: Map
    game_version: str
    game_length_in_ms: int
    started_at: datetime
    is_completed: bool
    queue: Queue
    season: Season
    platform: str
    premier: Optional[Dict]
    party_rr_penaltys: List[PartyPenalty]
    region: str
    cluster: str

class MatchDataV4(BaseModel):
    metadata: Metadata
    players: List[Player]
    observers: List[Observer]
    coaches: List[Coach]
    teams: List[Team]
    rounds: List[Round]
    kills: List[Kill]
