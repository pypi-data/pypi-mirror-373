from pydantic import BaseModel, HttpUrl

class BorderLevelModelResponse(BaseModel):
    uuid: str
    displayName: str
    startingLevel: int
    levelNumberAppearance: HttpUrl
    smallPlayerCardAppearance: HttpUrl
    assetPath: str