from pydantic import BaseModel


class DayMMRStats(BaseModel):
    mmr: int
    mmr_difference: int
    wins: int
    losses: int
    wins_percentage: float


class ShortPlayerStats(BaseModel):
    total_wins: int
    total_losses: int
    winrate: float
    kd: float
    adr: float
    most_picked_hero: str

    def __str__(self) -> str:
        return (
            f"ShortPlayerStats(record={self.total_wins}-{self.total_losses}, "
            f"winrate={self.winrate:.1f}%, kd={self.kd:.2f}, adr={self.adr:.1f}, most_picked_hero={self.most_picked_hero})"
        )


class MostPlayedHeroesStats(BaseModel):
    hero_id: str
    hero_name: str
    total_wins: int
    total_losses: int
    winrate: float
    kd: float

    def __str__(self) -> str:
        return (
            f"MostPlayedHeroesStats(hero={self.hero_name}, record={self.total_wins}-{self.total_losses}, "
            f"winrate={self.winrate:.1f}%, kd={self.kd:.2f})"
        )
