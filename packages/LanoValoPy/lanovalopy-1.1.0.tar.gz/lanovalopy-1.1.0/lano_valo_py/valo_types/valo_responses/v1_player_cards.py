from typing import Optional

from pydantic import BaseModel


class PlayerCardModelResponse(BaseModel):
    uuid: str
    displayName: Optional[str]
    isHiddenIfNotOwned: bool
    themeUuid: Optional[str]
    displayIcon: Optional[str]
    smallArt: Optional[str]
    wideArt: Optional[str]
    largeArt: Optional[str]
    assetPath: Optional[str]