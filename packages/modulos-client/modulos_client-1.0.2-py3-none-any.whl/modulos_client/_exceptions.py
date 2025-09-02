import requests

from typing import Literal


__all__ = [
    "BadRequestError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "UnprocessableEntityError",
    "InternalServerError",
]


class ModulosError(Exception):
    pass


class APIError(ModulosError):
    message: str
    request: requests.PreparedRequest | requests.Request | None

    body: object | None

    def __init__(
        self,
        message: str,
        request: requests.PreparedRequest | requests.Request | None,
        *,
        body: object | None,
    ) -> None:
        super().__init__(message)
        self.request = request
        self.message = message
        self.body = body


class APIStatusError(APIError):
    """Raised when an API response has a status code of 4xx or 5xx."""

    response: requests.Response
    status_code: int
    request_id: str | None

    def __init__(
        self, message: str, *, response: requests.Response, body: object | None
    ) -> None:
        super().__init__(message, response.request, body=body)
        self.response = response
        self.status_code = response.status_code
        self.request_id = response.headers.get("x-request-id")


class APIConnectionError(APIError):
    def __init__(
        self,
        *,
        message: str = "Connection error.",
        request: requests.PreparedRequest | requests.Request | None,
    ) -> None:
        super().__init__(message, request, body=None)


class APITimeoutError(APIConnectionError):
    def __init__(
        self, request: requests.PreparedRequest | requests.Request | None
    ) -> None:
        super().__init__(message="Request timed out.", request=request)


class BadRequestError(APIStatusError):
    status_code: Literal[400] = 400  # type: ignore


class AuthenticationError(APIStatusError):
    status_code: Literal[401] = 401  # type: ignore


class PermissionDeniedError(APIStatusError):
    status_code: Literal[403] = 403  # type: ignore


class NotFoundError(APIStatusError):
    status_code: Literal[404] = 404  # type: ignore


class UnprocessableEntityError(APIStatusError):
    status_code: Literal[422] = 422  # type: ignore


class InternalServerError(APIStatusError):
    pass
