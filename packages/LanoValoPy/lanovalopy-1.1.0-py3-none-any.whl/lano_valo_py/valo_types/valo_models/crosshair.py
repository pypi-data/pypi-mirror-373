from typing import Optional

from pydantic import BaseModel


class GetCrosshairFetchOptionsModel(BaseModel):
    code: str
    size: Optional[int] = None
