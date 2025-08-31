from typing import TypedDict


class DefaultHeaders(TypedDict, total=False):
    Accept: str
    Content_Type: str
    Authorization: str
    User_Agent: str
    X_Request_ID: str