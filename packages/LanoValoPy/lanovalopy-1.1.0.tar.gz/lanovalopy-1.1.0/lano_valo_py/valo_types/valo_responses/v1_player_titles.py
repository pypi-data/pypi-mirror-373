from typing import Optional

from pydantic import BaseModel


class PlayerTitleModelResponse(BaseModel):
    uuid: str
    displayName: Optional[str]
    titleText: Optional[str]
    isHiddenIfNotOwned: bool
    assetPath: Optional[str]

    def __str__(self):
        return f"PlayerTitleModelResponse(uuid={self.uuid}, displayName={self.displayName}, titleText={self.titleText})"
