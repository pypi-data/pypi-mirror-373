from typing import Optional

from pydantic import BaseModel

from ..valo_enums import Locales


class GetGameWeaponsModel(BaseModel):
    uuid: Optional[str] = None
    language: Optional[Locales] = Locales.ru_RU
