from abc import ABC
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from aiohttp import ClientResponse, ClientSession
from aiohttp.client_exceptions import ClientError, ContentTypeError

from .utils.const import CONTENT_TYPE, USER_AGENT
from .utils.types import DefaultHeaders
from .valo_types.valo_models import FetchOptionsModel
from .valo_types.valo_responses import APIResponseModel, ErrorObject, RateLimit


class BasedApi(ABC):
    def __init__(self, default_headers: Optional[DefaultHeaders] = {}):
        if default_headers:
            self.headers: Dict[str, str] = {
                "Accept": default_headers.get("Accept", CONTENT_TYPE),
                "Content-Type": default_headers.get("Content_Type", CONTENT_TYPE),
                "User-Agent": default_headers.get(
                    "User_Agent",
                    USER_AGENT,
                ),
            }

    async def _parse_body(self, body: Any) -> Any:
        """Parses the body of a response from the API.

        Checks if the response has an "errors" key, and if so, returns it.
        Otherwise, returns the "data" key if the response has a "status" key.
        Otherwise, returns the body as is.

        Args:
            body (Any): The body of the response.

        Returns:
            Any: The parsed body.
        """
        if "errors" in body:
            return body["errors"]
        return body["data"] if body.get("status") else body

    async def _parse_response(
        self, response: ClientResponse, url: str
    ) -> APIResponseModel:
        """Parses a response from the API into an APIResponseModel.

        Attempts to parse the body of the response as JSON and returns it.
        If the response is not 200 OK, returns the response status and an error message.
        If the response is 200 OK, returns the parsed body and the response status.
        """
        try:
            data = await response.json()
        except ContentTypeError:
            data = await response.text()

        ratelimits = None
        if "x-ratelimit-limit" in response.headers:
            ratelimits = RateLimit(
                used=int(response.headers.get("x-ratelimit-limit", 0)),
                remaining=int(response.headers.get("x-ratelimit-remaining", 0)),
                reset=int(response.headers.get("x-ratelimit-reset", 0)),
            )

        error = None
        if not response.ok:
            api_response = APIResponseModel(
                status=response.status,
                data=None,
                ratelimits=ratelimits,
                error=None,
                url=url,
            )
            try:
                error = ErrorObject(
                    message=data.get("errors", "Unknown error")[0].get(
                        "message", "Unknown error"
                    )
                )
                api_response.error = error
                return api_response

            except AttributeError:
                error = ErrorObject(message=str(data))
                api_response.error = error
                return api_response

        api_response = APIResponseModel(
            status=response.status,
            data=None
            if "application/json" not in response.headers.get("Content-Type", "")
            else await self._parse_body(data),
            ratelimits=ratelimits,
            error=error,
            url=url,
        )
        return api_response

    def _validate(self, input_data: Dict[str, Any], required_fields: List[str] = []):
        """
        Validates the input data for required fields.

        Args:
            input_data (Dict[str, Any]): The data to be validated.
            required_fields (List[str], optional): The fields that must be present in input_data. Defaults to None.

        Raises:
            ValueError: If any of the required fields are missing from input_data.
        """
        required_fields = required_fields or []

        for key, value in input_data.items():
            if key in required_fields and value is None:
                raise ValueError(f"Missing required parameter: {key}")

    def _query(self, input_data: Dict[str, Any]) -> Optional[str]:
        """
        Takes a dictionary of query parameters and turns them into a URL query string.

        Args:
            input_data (Dict[str, Any]): The query parameters to be converted into a URL query string.

        Returns:
            Optional[str]: The URL query string, or None if the input_data is empty.
        """
        query_params = {
            k: ("true" if v is True else "false" if v is False else v)
            for k, v in input_data.items()
            if v is not None
        }
        return urlencode(query_params) if query_params else None

    async def _fetch(self, fetch_options: FetchOptionsModel) -> APIResponseModel:
        """
        Performs an asynchronous HTTP request based on the provided FetchOptionsModel.

        Args:
            fetch_options (FetchOptionsModel): The options for the HTTP request.

        Returns:
            APIResponseModel: The response to the HTTP request, or an error response if the request fails.
        """
        method = fetch_options.type.upper()
        url = fetch_options.url
        headers = self.headers.copy()

        if fetch_options.type == "POST" and fetch_options.body:
            json_data = fetch_options.body
        else:
            json_data = None

        try:
            async with ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    headers=headers,
                    json=json_data,
                    params=None if not fetch_options.rtype else fetch_options.rtype,
                ) as response:
                    if fetch_options.rtype == "arraybuffer":
                        data = await response.read()
                        return APIResponseModel(
                            status=201,
                            data=data,
                        )

                    return await self._parse_response(response, url)
        except ClientError as e:
            return APIResponseModel(
                status=500,
                data=[],
                ratelimits=None,
                error=ErrorObject(message=str(e)),
                url=fetch_options.url,
            )
