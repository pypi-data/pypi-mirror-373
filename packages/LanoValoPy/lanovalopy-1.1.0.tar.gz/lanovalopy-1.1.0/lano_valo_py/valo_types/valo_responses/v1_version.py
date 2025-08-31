from pydantic import BaseModel


class BuildGameInfoResponseModel(BaseModel):
    region: str
    branch: str
    build_date: str
    build_ver: str
    last_checked: str
    version: int
    version_for_api: str
