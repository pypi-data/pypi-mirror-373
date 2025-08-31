from typing import List, Optional

from pydantic import BaseModel

from .v1_mmr_history import MapModel


class ContnentLocalizedNamesResponseModel(BaseModel):
    ar_AE: Optional[str] = None
    de_DE: Optional[str] = None
    en_GB: Optional[str] = None
    en_US: Optional[str] = None
    es_ES: Optional[str] = None
    es_MX: Optional[str] = None
    fr_FR: Optional[str] = None
    id_ID: Optional[str] = None
    it_IT: Optional[str] = None
    ja_JP: Optional[str] = None
    ko_KR: Optional[str] = None
    pl_PL: Optional[str] = None
    pt_BR: Optional[str] = None
    ru_RU: Optional[str] = None
    th_TH: Optional[str] = None
    tr_TR: Optional[str] = None
    vi_VN: Optional[str] = None
    zn_CN: Optional[str] = None
    zn_TW: Optional[str] = None


class CharacterContentResponseModel(BaseModel):
    name: str
    localizedNames: Optional[List[ContnentLocalizedNamesResponseModel]]
    id: str
    assetName: Optional[str] = None
    assetPath: Optional[str] = None


class ContentMapResponseModel(BaseModel):
    name: str
    localizedNames: Optional[List[ContnentLocalizedNamesResponseModel]]
    id: str
    assetName: Optional[str] = None
    assetPath: Optional[str] = None


class ContentChromaResponseModel(BaseModel):
    name: str
    localizedNames: Optional[List[ContnentLocalizedNamesResponseModel]]
    id: str
    assetName: Optional[str] = None
    assetPath: Optional[str] = None


class ContentSkinResponseModel(BaseModel):
    name: str
    localizedNames: Optional[List[ContnentLocalizedNamesResponseModel]]
    id: str
    assetName: Optional[str] = None
    assetPath: Optional[str] = None


class ContentSkinLevelResponseModel(BaseModel):
    name: str
    localizedNames: Optional[List[ContnentLocalizedNamesResponseModel]]
    id: str
    assetName: Optional[str] = None
    assetPath: Optional[str] = None


class ContentEquipResponseModel(BaseModel):
    name: str
    localizedNames: Optional[List[ContnentLocalizedNamesResponseModel]]
    id: str
    assetName: Optional[str] = None
    assetPath: Optional[str] = None


class ContentGameModeResponseModel(BaseModel):
    name: str
    localizedNames: Optional[List[ContnentLocalizedNamesResponseModel]]
    id: str
    assetName: Optional[str] = None
    assetPath: Optional[str] = None


class ContentSprayResponseModel(BaseModel):
    name: str
    localizedNames: Optional[List[ContnentLocalizedNamesResponseModel]]
    id: str
    assetName: Optional[str] = None
    assetPath: Optional[str] = None


class ContentSprayLeveResonselModel(BaseModel):
    name: str
    localizedNames: Optional[List[ContnentLocalizedNamesResponseModel]]
    id: str
    assetName: Optional[str] = None
    assetPath: Optional[str] = None


class ContentCharmResponseModel(BaseModel):
    name: str
    localizedNames: Optional[List[ContnentLocalizedNamesResponseModel]]
    id: str
    assetName: Optional[str] = None
    assetPath: Optional[str] = None


class ContentCharmLeveResonsellModel(BaseModel):
    name: str
    localizedNames: Optional[List[ContnentLocalizedNamesResponseModel]]
    id: str
    assetName: Optional[str] = None
    assetPath: Optional[str] = None


class ContetnPlayerCardResponseModel(BaseModel):
    name: str
    localizedNames: Optional[List[ContnentLocalizedNamesResponseModel]]
    id: str
    assetName: Optional[str] = None
    assetPath: Optional[str] = None


class ContentPlayerTitleResponseModel(BaseModel):
    name: str
    localizedNames: Optional[List[ContnentLocalizedNamesResponseModel]]
    id: str
    assetName: Optional[str] = None
    assetPath: Optional[str] = None


class ContentActResponseModel(BaseModel):
    name: str
    localizedNames: Optional[List[ContnentLocalizedNamesResponseModel]]
    id: str
    isActive: bool


class ContentResponseModel(BaseModel):
    version: str
    characters: List[ContnentLocalizedNamesResponseModel]
    maps: List[MapModel]
    chromas: List[ContentCharmResponseModel]
    skins: List[ContentSkinResponseModel]
    skinLevels: List[ContentSkinLevelResponseModel]
    equips: List[ContentEquipResponseModel]
    gameModes: List[ContentGameModeResponseModel]
    sprays: List[ContentSprayResponseModel]
    sprayLevels: List[ContentSprayLeveResonselModel]
    charms: List[ContentCharmResponseModel]
    charmLevels: List[ContentCharmLeveResonsellModel]
    playerCards: List[ContetnPlayerCardResponseModel]
    playerTitles: List[ContentPlayerTitleResponseModel]
    acts: List[ContentActResponseModel]
