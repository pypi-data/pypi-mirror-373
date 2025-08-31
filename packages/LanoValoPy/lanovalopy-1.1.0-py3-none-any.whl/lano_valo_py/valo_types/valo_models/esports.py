from typing import Optional

from pydantic import BaseModel

from ..valo_enums import EsportsLeagues, EsportsRegions


class GetEsportsMatchesFetchOptionsModel(BaseModel):
    region: Optional[EsportsRegions] = None
    league: Optional[EsportsLeagues] = None
