from typing import Optional

from pydantic import BaseModel

from ..valo_enums import AccountVersion


class AccountFetchOptionsModel(BaseModel):
    name: str
    tag: str
    version: AccountVersion = AccountVersion.v1
    force: Optional[bool] = None


class AccountFetchByPUUIDOptionsModel(BaseModel):
    puuid: str
    force: Optional[bool] = None


class AccountFetchOptionsModelV2(BaseModel):
    name: Optional[str] = None
    tag: Optional[str] = None
    puuid: Optional[str] = None
    force: Optional[bool] = None