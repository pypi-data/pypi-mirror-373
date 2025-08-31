from pydantic import BaseModel


class AccountCardResponseModelV1(BaseModel):
    small: str
    large: str
    wide: str
    id: str


class AccountResponseModelV1(BaseModel):
    puuid: str
    region: str
    account_level: int
    name: str
    tag: str
    card: AccountCardResponseModelV1
    last_update: str
    last_update_raw: int

    class Config:
        extra = "ignore"

    def __str__(self):
        fields = "\n".join(
            f"{key}={value!r}" for key, value in self.model_dump().items()
        )
        return f"{self.__class__.__name__}(\n{fields}\n)"