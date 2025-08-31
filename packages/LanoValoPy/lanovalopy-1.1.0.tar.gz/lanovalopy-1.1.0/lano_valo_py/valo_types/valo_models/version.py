from pydantic import BaseModel

from ..valo_enums import Regions


class GetVersionFetchOptionsModel(BaseModel):
    region: Regions
