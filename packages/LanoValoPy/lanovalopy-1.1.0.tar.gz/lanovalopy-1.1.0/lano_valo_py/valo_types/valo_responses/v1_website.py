from typing import Optional

from pydantic import BaseModel


class CommunityNewsResponseModel(BaseModel):
    banner_url: str
    category: str
    date: str
    external_link: Optional[str]
    title: str
    url: str
