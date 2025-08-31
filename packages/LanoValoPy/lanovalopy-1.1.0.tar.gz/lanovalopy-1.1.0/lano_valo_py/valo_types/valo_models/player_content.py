from typing import Optional

from pydantic import BaseModel

from ..valo_enums import Locales


class GetPlayerCardModel(BaseModel):
    uuid: Optional[str] = None
    language: Optional[Locales] = Locales.en_US


class GetPlayerTitleModel(BaseModel):
    uuid: Optional[str] = None
    language: Optional[Locales] = Locales.en_US
