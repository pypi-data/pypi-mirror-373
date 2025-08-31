from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class RoleAgentResponseModel(BaseModel):
    uuid: str
    displayName: str
    description: str
    displayIcon: Optional[HttpUrl]
    assetPath: str


class AbilityAgentResponseModel(BaseModel):
    slot: str
    displayName: str
    description: str
    displayIcon: Optional[HttpUrl]


class AgentResponseModel(BaseModel):
    uuid: str
    displayName: str
    description: str
    developerName: str
    characterTags: Optional[List[str]]
    displayIcon: Optional[HttpUrl]
    displayIconSmall: Optional[HttpUrl]
    bustPortrait: Optional[HttpUrl]
    fullPortrait: Optional[HttpUrl]
    fullPortraitV2: Optional[HttpUrl]
    killfeedPortrait: Optional[HttpUrl]
    background: Optional[HttpUrl]
    backgroundGradientColors: List[str]
    assetPath: str
    isFullPortraitRightFacing: bool
    isPlayableCharacter: bool
    isAvailableForTest: bool
    isBaseContent: bool
    role: Optional[RoleAgentResponseModel]
    recruitmentData: Optional[dict]
    abilities: List[AbilityAgentResponseModel]
    voiceLine: Optional[dict]
