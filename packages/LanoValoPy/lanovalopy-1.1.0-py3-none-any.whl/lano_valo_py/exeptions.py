from .valo_types.valo_responses import APIResponseModel


class UnauthorizedError(Exception):
    def __init__(self, message: str, response: APIResponseModel):
        super().__init__(message)
        self.response = response
    
    def __str__(self):
        return f"UnauthorizedError: {self.response.error}\n" + \
        f"status:{self.response.status}\n" + \
        f"url:{self.response.url}\n" + \
        f"ratelimit:{self.response.ratelimits}"

