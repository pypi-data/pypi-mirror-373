from typing import List, Optional

from pydantic import BaseModel


class TranslationResponseModel(BaseModel):
    content: str
    locale: str


class UpdateStatusResponseModel(BaseModel):
    created_at: str
    updated_at: str
    publish: bool
    id: int
    translations: List[TranslationResponseModel]
    publish_locations: List[str]
    author: str


class StatusTitleResponseModel(BaseModel):
    content: str
    locale: str


class StatusMaintenanceResponseModel(BaseModel):
    created_at: str
    archive_at: str
    updates: List[UpdateStatusResponseModel]
    platforms: List[str]
    updated_at: str
    id: int
    titles: List[StatusTitleResponseModel]
    maintenance_status: str
    incident_severity: str


class StatusIncidentResponseModel(BaseModel):
    created_at: str
    archive_at: str
    updates: List[UpdateStatusResponseModel]
    platforms: List[str]
    updated_at: str
    id: int
    titles: List[StatusTitleResponseModel]
    maintenance_status: str
    incident_severity: str


class StatusDataResponseModel(BaseModel):
    maintenances: Optional[List[StatusMaintenanceResponseModel]]
    incidents: Optional[List[StatusIncidentResponseModel]]