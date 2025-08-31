from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class LocationMapModelResponse(BaseModel):
    x: float
    y: float


class CalloutMapModelResponse(BaseModel):
    regionName: str
    superRegionName: str
    location: LocationMapModelResponse


class MapModelResponse(BaseModel):
    uuid: str
    displayName: str
    narrativeDescription: Optional[str]
    tacticalDescription: Optional[str]
    coordinates: Optional[str]
    displayIcon: Optional[HttpUrl]
    listViewIcon: Optional[HttpUrl]
    listViewIconTall: Optional[HttpUrl]
    splash: Optional[HttpUrl]
    stylizedBackgroundImage: Optional[HttpUrl]
    premierBackgroundImage: Optional[HttpUrl]
    assetPath: str
    mapUrl: str
    xMultiplier: float
    yMultiplier: float
    xScalarToAdd: float
    yScalarToAdd: float
    callouts: Optional[List[CalloutMapModelResponse]]
