import json
import os

import requests

from . import _exceptions, resources

__all__ = [
    "Modulos",
]


class Modulos:
    testing: resources.Testing
    evidence: resources.Evidence

    HEADERS = {
        "User-Agent": "modulos-client/1.0.0 (Modulos Client)",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
    }

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:

        if api_key is None:
            api_key = os.environ.get("MODULOS_API_KEY")
        if api_key is None:
            raise _exceptions.ModulosError(
                "The api_key client option must be set either by passing "
                "api_key to the client "
                "or by setting the MODULOS_API_KEY environment variable"
            )

        self.api_key = api_key

        if base_url is None:
            base_url = "https://app.modulos.ai/api"
        self.base_url = base_url

        self.testing = resources.Testing(self)
        self.evidence = resources.Evidence(self)

    def _add_prefix_to_endpoint(self, endpoint: str) -> str:
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        return endpoint

    def _get_headers(self) -> dict[str, str]:
        return self.HEADERS | {"Authorization": f"Bearer {self.api_key}"}

    def post(
        self,
        endpoint: str,
        url_params: dict | None = None,
        data: dict | None = None,
        files: dict | None = None,
    ):
        try:
            endpoint = self._add_prefix_to_endpoint(endpoint)
            api_url = f"{self.base_url}{endpoint}"

            if url_params:
                api_url += "?" + "&".join([f"{k}={v}" for k, v in url_params.items()])

            response = requests.post(
                api_url,
                headers=self._get_headers(),
                json=data,
                files=files,
            )
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as err:
            raise self._make_status_error_from_response(err.response) from None
        except requests.exceptions.ReadTimeout as err:
            raise _exceptions.APITimeoutError(request=err.request) from err
        except requests.exceptions.ConnectionError as err:
            raise _exceptions.APIConnectionError(request=err.request) from err
        except requests.exceptions.RequestException as err:
            raise _exceptions.APIError(
                message="An unknown error occurred.",
                request=err.request,
                body=None,
            ) from err

    def get(self, endpoint: str):
        try:
            endpoint = self._add_prefix_to_endpoint(endpoint)
            api_url = f"{self.base_url}{endpoint}"
            response = requests.get(
                api_url,
                headers=self._get_headers(),
            )

            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as err:
            raise self._make_status_error_from_response(err.response) from None
        except requests.exceptions.ReadTimeout as err:
            raise _exceptions.APITimeoutError(request=err.request) from err
        except requests.exceptions.ConnectionError as err:
            raise _exceptions.APIConnectionError(request=err.request) from err
        except requests.exceptions.RequestException as err:
            raise _exceptions.APIError(
                message="An unknown error occurred.",
                request=err.request,
                body=None,
            ) from err

    def delete(
        self,
        endpoint: str,
    ):
        try:
            endpoint = self._add_prefix_to_endpoint(endpoint)
            api_url = f"{self.base_url}{endpoint}"

            response = requests.delete(
                api_url,
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as err:
            raise self._make_status_error_from_response(err.response) from None
        except requests.exceptions.ReadTimeout as err:
            raise _exceptions.APITimeoutError(request=err.request) from err
        except requests.exceptions.ConnectionError as err:
            raise _exceptions.APIConnectionError(request=err.request) from err
        except requests.exceptions.RequestException as err:
            raise _exceptions.APIError(
                message="An unknown error occurred.",
                request=err.request,
                body=None,
            ) from err

    def patch(self, endpoint: str, data: dict):
        try:
            endpoint = self._add_prefix_to_endpoint(endpoint)
            api_url = f"{self.base_url}{endpoint}"
            response = requests.patch(
                url=api_url,
                headers=self._get_headers(),
                json=data,
            )
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as err:
            raise self._make_status_error_from_response(err.response) from None
        except requests.exceptions.ReadTimeout as err:
            raise _exceptions.APITimeoutError(request=err.request) from err
        except requests.exceptions.ConnectionError as err:
            raise _exceptions.APIConnectionError(request=err.request) from err
        except requests.exceptions.RequestException as err:
            raise _exceptions.APIError(
                message="An unknown error occurred.",
                request=err.request,
                body=None,
            ) from err

    def _make_status_error_from_response(self, response: requests.Response):
        err_text = response.text.strip()
        body = err_text

        try:
            body = json.loads(err_text)
            err_msg = f"Error code: {response.status_code} - {body}"
        except Exception:
            err_msg = err_text or f"Error code: {response.status_code}"

        return self._make_status_error(err_msg=err_msg, body=body, response=response)

    def _make_status_error(
        self,
        err_msg: str,
        body: object,
        response: requests.Response,
    ) -> _exceptions.APIStatusError:
        data = body
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=data)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(
                err_msg, response=response, body=data
            )

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(
                err_msg, response=response, body=data
            )

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=data)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(
                err_msg, response=response, body=data
            )

        if response.status_code >= 500:
            return _exceptions.InternalServerError(
                err_msg, response=response, body=data
            )
        return _exceptions.APIStatusError(err_msg, response=response, body=data)
