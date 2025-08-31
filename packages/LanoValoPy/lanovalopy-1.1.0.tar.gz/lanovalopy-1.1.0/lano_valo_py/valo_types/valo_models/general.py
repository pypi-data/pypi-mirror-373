from typing import Any, Dict, Optional

from pydantic import BaseModel


class FetchOptionsModel(BaseModel):
    url: str
    type: str = "GET"
    body: Optional[Dict[str, Any]] = None
    rtype: Optional[str] = None
