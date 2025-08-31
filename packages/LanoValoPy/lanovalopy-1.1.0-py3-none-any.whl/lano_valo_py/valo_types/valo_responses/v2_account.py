from typing import List, Literal
from pydantic import BaseModel


class AccountResponseModelV2(BaseModel):
    puuid: str
    region: str
    account_level: int
    name: str
    tag: str
    title: str
    card: str
    platforms: List[Literal["PC", "CONSOLE"]]  # noqa: F821

    class Config:
        extra = "ignore"

    def __str__(self):
        fields = "\n".join(
            f"{key}={value!r}" for key, value in self.model_dump().items()
        )
        return f"{self.__class__.__name__}(\n{fields}\n)"