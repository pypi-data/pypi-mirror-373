from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class AdsStatsGameWeaponResponseModel(BaseModel):
    zoomMultiplier: float
    fireRate: float
    runSpeedMultiplier: float
    burstCount: int
    firstBulletAccuracy: float


class DamageRangeGameWeaponResponseModel(BaseModel):
    rangeStartMeters: int
    rangeEndMeters: int
    headDamage: float
    bodyDamage: float
    legDamage: float


class WeaponStatsGameWeaponResponseModel(BaseModel):
    fireRate: float
    magazineSize: int
    runSpeedMultiplier: float
    equipTimeSeconds: float
    reloadTimeSeconds: float
    firstBulletAccuracy: float
    shotgunPelletCount: int
    wallPenetration: str
    feature: Optional[str]
    fireMode: Optional[str] = None
    altFireType: Optional[str]
    adsStats: Optional[AdsStatsGameWeaponResponseModel]
    altShotgunStats: Optional[dict] = None
    airBurstStats: Optional[dict] = None
    damageRanges: List[DamageRangeGameWeaponResponseModel]


class GridPositionGameWeaponResponseModel(BaseModel):
    row: int
    column: int


class WeaponShopInfoGameWeaponResponseModel(BaseModel):
    cost: int
    category: str
    shopOrderPriority: int
    categoryText: str
    gridPosition: GridPositionGameWeaponResponseModel
    canBeTrashed: bool
    image: Optional[str] = None
    newImage: Optional[str] = None
    newImage2: Optional[str] = None
    assetPath: str

class ChromaGameWeaponResponseModel(BaseModel):
    uuid: str
    displayName: str
    displayIcon: Optional[HttpUrl] = None
    fullRender: Optional[HttpUrl] = None
    swatch: Optional[HttpUrl] = None
    streamedVideo: Optional[HttpUrl] = None
    assetPath: str

class LevelGameWeaponResponseModel(BaseModel):
    uuid: str
    displayName: str
    levelItem: Optional[str] = None
    displayIcon: Optional[HttpUrl] = None
    streamedVideo: Optional[HttpUrl] = None
    assetPath: str

class WeaponSkinGameWeaponResponseModel(BaseModel):
    uuid: str
    displayName: str
    themeUuid: str
    contentTierUuid: str
    displayIcon: HttpUrl
    wallpaper: Optional[HttpUrl] = None
    assetPath: str
    chromas: List[ChromaGameWeaponResponseModel]
    levels: List[LevelGameWeaponResponseModel]


class WeaponResponseModel(BaseModel):
    uuid: str
    displayName: str
    category: str
    defaultSkinUuid: str
    displayIcon: Optional[HttpUrl]
    killStreamIcon: Optional[HttpUrl]
    assetPath: str
    weaponStats: WeaponStatsGameWeaponResponseModel
    shopData: WeaponShopInfoGameWeaponResponseModel
    skins: Optional[List[WeaponSkinGameWeaponResponseModel]]
