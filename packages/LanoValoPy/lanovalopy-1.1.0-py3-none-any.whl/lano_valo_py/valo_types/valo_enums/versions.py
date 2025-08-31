from enum import Enum


class MMRVersions(str, Enum):
    v1 = "v1"
    v2 = "v2"
    v3 = "v3"


class MMRHistoryVersions(str, Enum):
    v1 = "v1"
    v2 = "v2"


class FeaturedItemsVersion(str, Enum):
    v1 = "v1"
    v2 = "v2"


class LeaderboardVersions(str, Enum):
    v1 = "v1"
    v2 = "v2"
    v3 = "v3"


class AccountVersion(str, Enum):
    v1 = "v1"
    v2 = "v2"


class MatchListVersion(str, Enum):
    v3 = "v3"
    v4 = "v4"

class MatchVersion(str, Enum):
    v3 = "v2"
    v4 = "v4"