from typing import Optional

from pydantic import BaseModel

from ..valo_enums import Locales


class GetContentFetchOptionsModel(BaseModel):
    locale: Optional[Locales] = None
