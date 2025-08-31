from typing import Any, Dict, List, NewType, Optional

from pydantic import BaseModel

BinaryData = NewType("BinaryData", bytes)


class RateLimit(BaseModel):
    used: int
    remaining: int
    reset: int


class ErrorObject(BaseModel):
    message: str


class APIResponseModel(BaseModel):
    status: int
    data: Optional[Dict[str, Any]] | Optional[List[Dict[str, Any]]] | bytes = None
    ratelimits: Optional[RateLimit] = None
    error: Optional[ErrorObject] = None
    url: Optional[str] = None
