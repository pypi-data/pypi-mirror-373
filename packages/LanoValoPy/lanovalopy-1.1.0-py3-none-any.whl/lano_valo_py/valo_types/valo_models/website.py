from typing import Optional

from pydantic import BaseModel

from ..valo_enums import CCRegions


class GetWebsiteFetchOptionsModel(BaseModel):
    country_code: CCRegions
    filter: Optional[str] = None
