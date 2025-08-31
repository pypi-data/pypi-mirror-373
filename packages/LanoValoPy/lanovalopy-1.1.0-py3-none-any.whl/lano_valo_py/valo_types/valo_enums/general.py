from enum import Enum


class Modes(str, Enum):
    escalation = "escalation"
    spikerush = "spikerush"
    deathmatch = "deathmatch"
    competitive = "competitive"
    unrated = "unrated"
    replication = "replication"
    custom = "custom"
    newmap = "newmap"
    snowballfight = "snowballfight"
    teamdeathmatch = "teamdeathmatch"
    swiftplay = "swiftplay"

class Maps(Enum):
    ascent = "ascent"
    split = "split"
    fracture = "fracture"
    bind = "bind"
    breeze = "breeze"
    district = "district"
    kasbah = "kasbah"
    piazza = "piazza"
    lotus = "lotus"
    pearl = "pearl"
    icebox = "icebox"
    haven = "haven"

    def __str__(self):
        return self.value


class RawTypes(str, Enum):
    competitiveupdates = "competitiveupdates"
    mmr = "mmr"
    matchdetails = "matchdetails"
    matchhistory = "matchhistory"


class Patforms(str, Enum):
    pc = "PC"
    console = "CONSOLE"
