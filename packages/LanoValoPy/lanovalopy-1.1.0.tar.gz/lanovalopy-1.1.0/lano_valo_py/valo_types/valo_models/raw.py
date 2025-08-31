from pydantic import BaseModel

from ..valo_enums import RawTypes, Regions


class GetRawFetchOptionsModel(BaseModel):
    type: RawTypes
    uuid: str
    region: Regions
    queries: str
