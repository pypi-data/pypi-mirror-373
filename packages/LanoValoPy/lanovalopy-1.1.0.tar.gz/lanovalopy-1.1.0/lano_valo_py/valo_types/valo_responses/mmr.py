from typing import Dict, List, Optional, Union

from pydantic import BaseModel


class ActRankWinsModel(BaseModel):
    patched_tier: str
    tier: int


class SeasonDataModel(BaseModel):
    error: Optional[Union[bool, str]] = None
    wins: Optional[int] = None
    number_of_games: Optional[int] = None
    final_rank: Optional[int] = None
    final_rank_patched: Optional[str] = None
    act_rank_wins: Optional[List[ActRankWinsModel]] = None
    old: Optional[bool] = None


class ImagesModel(BaseModel):
    small: str
    large: str
    triangle_down: str
    triangle_up: str


class CurrentDataModel(BaseModel):
    currenttier: Optional[int]
    currenttierpatched: Optional[str]
    images: ImagesModel
    ranking_in_tier: Optional[int]
    mmr_change_to_last_game: Optional[int]
    elo: Optional[int]
    old: bool


class HighestRankModel(BaseModel):
    old: bool
    tier: Optional[int]
    patched_tier: str
    season: Optional[str]


class MMRResponseModel(BaseModel):
    name: str
    tag: str
    current_data: Optional[CurrentDataModel] = None
    highest_rank: Optional[HighestRankModel] = None
    by_season: Optional[Dict[str, SeasonDataModel]] = None

    def __str__(self):
        fields = "\n".join(
            f"{key}={value!r}" for key, value in self.model_dump().items()
        )
        return f"{self.__class__.__name__}(\n{fields}\n)"
