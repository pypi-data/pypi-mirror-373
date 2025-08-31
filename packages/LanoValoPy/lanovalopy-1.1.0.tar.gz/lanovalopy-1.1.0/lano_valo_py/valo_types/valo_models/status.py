from pydantic import BaseModel

from ..valo_enums import Regions


class GetStatusFetchOptionsModel(BaseModel):
    region: Regions
