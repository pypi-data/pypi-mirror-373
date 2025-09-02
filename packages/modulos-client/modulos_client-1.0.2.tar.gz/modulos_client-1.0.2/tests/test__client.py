import os
import pytest
import responses
import requests

from responses import matchers


from modulos_client import Modulos, ModulosError, _exceptions


def test_init_with_api_key():
    # when
    modulos = Modulos(api_key="test_api_key")

    # then
    assert modulos.api_key == "test_api_key"
    assert modulos.base_url == "https://app.modulos.ai/api"


def test_init_with_api_key_with_environment_variable(monkeypatch):
    # given
    monkeypatch.setenv("MODULOS_API_KEY", "1234")

    # when
    modulos = Modulos()

    # then
    assert modulos.api_key == os.environ.get("MODULOS_API_KEY")
    assert modulos.base_url == "https://app.modulos.ai/api"


def test_init_with_base_url(monkeypatch):
    # given
    base_url = "https://example.com/api"
    monkeypatch.setenv("MODULOS_API_KEY", "1234")

    # when
    modulos = Modulos(base_url=base_url)

    # then
    assert modulos.api_key == os.environ.get("MODULOS_API_KEY")
    assert modulos.base_url == base_url


def test_init_with_api_key_and_base_url():
    # given
    base_url = "https://example.com/api"
    api_url = "test_api_key"

    # when
    modulos = Modulos(api_key=api_url, base_url=base_url)

    # then
    assert modulos.api_key == api_url
    assert modulos.base_url == base_url


def test_init_with_no_api_key():
    # when
    with pytest.raises(ModulosError) as exc_info:
        Modulos()

    # then
    assert "MODULOS_API_KEY" in str(exc_info.value)


# POST
@responses.activate
def test_post(modulos):
    # given
    response_post = responses.Response(
        method="POST",
        url=f"{modulos.base_url}/endpoint",
        json={"key": "value"},
        status=200,
    )
    responses.add(response_post)

    # when
    response = modulos.post("/endpoint", data={"key": "value"})

    # then
    assert response.status_code == 200
    assert response.json() == {"key": "value"}


@responses.activate
def test_post__url_params(modulos):
    # given
    url_params = {"param_1": "value1", "param_2": "value2"}

    response_post = responses.Response(
        method="POST",
        url=f"{modulos.base_url}/endpoint",
        json={"key": "value"},
        status=200,
        match=[matchers.query_param_matcher(url_params)],
    )
    responses.add(response_post)

    # when

    response = modulos.post("/endpoint", data={"key": "value"}, url_params=url_params)

    # then
    assert response.status_code == 200
    assert response.json() == {"key": "value"}
    assert response.request.params == url_params


@responses.activate
def test_post_http_error(modulos):
    # given

    response_post = responses.Response(
        method="POST",
        url=f"{modulos.base_url}/endpoint",
        json={"key": "value"},
        status=404,
    )
    responses.add(response_post)

    # when
    with pytest.raises(_exceptions.APIStatusError) as exc_info:
        modulos.post("/endpoint", data={"key": "value"})

    # then
    assert exc_info.value.status_code == 404
    assert exc_info.value.request_id is None
    assert isinstance(exc_info.value.response, requests.Response)


@responses.activate
def test_post_timeout_error(modulos):
    # given

    response_post = responses.Response(
        method="POST",
        url=f"{modulos.base_url}/endpoint",
        body=requests.exceptions.ReadTimeout(),
    )
    responses.add(response_post)

    # when
    with pytest.raises(_exceptions.APITimeoutError) as exc_info:
        modulos.post("/endpoint")

    # then
    assert exc_info.value.request is not None
    assert exc_info.value.body is None
    assert "Request timed out." in str(exc_info.value)


@responses.activate
def test_post_connection_error(modulos):
    # given

    response_post = responses.Response(
        method="POST",
        url=f"{modulos.base_url}/endpoint",
        body=requests.exceptions.ConnectionError(),
    )
    responses.add(response_post)

    # when
    with pytest.raises(_exceptions.APIConnectionError) as exc_info:
        modulos.post("/endpoint")

    # then
    assert exc_info.value.request is not None
    assert exc_info.value.body is None
    assert "Connection error." in str(exc_info.value)


@responses.activate
def test_post_api_error(modulos):
    # given

    response_post = responses.Response(
        method="POST",
        url=f"{modulos.base_url}/endpoint",
        body=requests.exceptions.RequestException(),
    )
    responses.add(response_post)

    # when
    with pytest.raises(_exceptions.APIError) as exc_info:
        modulos.post("/endpoint")

    # then
    assert exc_info.value.request is not None
    assert exc_info.value.body is None
    assert "An unknown error occurred." in str(exc_info.value)


# GET
@responses.activate
def test_get(modulos):
    # given
    response_get = responses.Response(
        method="GET",
        url=f"{modulos.base_url}/endpoint",
        status=200,
    )
    responses.add(response_get)

    # when
    response = modulos.get("/endpoint")

    # then
    assert response.status_code == 200


@responses.activate
def test_get_http_error(modulos):
    # given

    response_get = responses.Response(
        method="GET",
        url=f"{modulos.base_url}/endpoint",
        status=404,
    )
    responses.add(response_get)

    # when
    with pytest.raises(_exceptions.APIStatusError) as exc_info:
        modulos.get("/endpoint")

    # then
    assert exc_info.value.status_code == 404
    assert exc_info.value.request_id is None
    assert isinstance(exc_info.value.response, requests.Response)


@responses.activate
def test_get_timeout_error(modulos):
    # given

    response_get = responses.Response(
        method="GET",
        url=f"{modulos.base_url}/endpoint",
        body=requests.exceptions.ReadTimeout(),
    )
    responses.add(response_get)

    # when
    with pytest.raises(_exceptions.APITimeoutError) as exc_info:
        modulos.get("/endpoint")

    # then
    assert exc_info.value.request is not None
    assert exc_info.value.body is None
    assert "Request timed out." in str(exc_info.value)


@responses.activate
def test_get_connection_error(modulos):
    # given

    response_get = responses.Response(
        method="GET",
        url=f"{modulos.base_url}/endpoint",
        body=requests.exceptions.ConnectionError(),
    )
    responses.add(response_get)

    # when
    with pytest.raises(_exceptions.APIConnectionError) as exc_info:
        modulos.get("/endpoint")

    # then
    assert exc_info.value.request is not None
    assert exc_info.value.body is None
    assert "Connection error." in str(exc_info.value)


@responses.activate
def test_get_api_error(modulos):
    # given

    response_get = responses.Response(
        method="GET",
        url=f"{modulos.base_url}/endpoint",
        body=requests.exceptions.RequestException(),
    )
    responses.add(response_get)

    # when
    with pytest.raises(_exceptions.APIError) as exc_info:
        modulos.get("/endpoint")

    # then
    assert exc_info.value.request is not None
    assert exc_info.value.body is None
    assert "An unknown error occurred." in str(exc_info.value)


# DELETE
@responses.activate
def test_delete(modulos):
    # given
    response_delete = responses.Response(
        method="DELETE",
        url=f"{modulos.base_url}/endpoint",
        status=204,
    )
    responses.add(response_delete)

    # when
    response = modulos.delete("/endpoint")

    # then
    assert response.status_code == 204


@responses.activate
def test_delete_http_error(modulos):
    # given

    response_delete = responses.Response(
        method="DELETE",
        url=f"{modulos.base_url}/endpoint",
        status=404,
    )
    responses.add(response_delete)

    # when
    with pytest.raises(_exceptions.APIStatusError) as exc_info:
        modulos.delete("/endpoint")

    # then
    assert exc_info.value.status_code == 404
    assert exc_info.value.request_id is None
    assert isinstance(exc_info.value.response, requests.Response)


@responses.activate
def test_delete_timeout_error(modulos):
    # given

    response_delete = responses.Response(
        method="DELETE",
        url=f"{modulos.base_url}/endpoint",
        body=requests.exceptions.ReadTimeout(),
    )
    responses.add(response_delete)

    # when
    with pytest.raises(_exceptions.APITimeoutError) as exc_info:
        modulos.delete("/endpoint")

    # then
    assert exc_info.value.request is not None
    assert exc_info.value.body is None
    assert "Request timed out." in str(exc_info.value)


@responses.activate
def test_delete_connection_error(modulos):
    # given

    response_delete = responses.Response(
        method="DELETE",
        url=f"{modulos.base_url}/endpoint",
        body=requests.exceptions.ConnectionError(),
    )
    responses.add(response_delete)

    # when
    with pytest.raises(_exceptions.APIConnectionError) as exc_info:
        modulos.delete("/endpoint")

    # then
    assert exc_info.value.request is not None
    assert exc_info.value.body is None
    assert "Connection error." in str(exc_info.value)


@responses.activate
def test_delete_api_error(modulos):
    # given

    response_delete = responses.Response(
        method="DELETE",
        url=f"{modulos.base_url}/endpoint",
        body=requests.exceptions.RequestException(),
    )
    responses.add(response_delete)

    # when
    with pytest.raises(_exceptions.APIError) as exc_info:
        modulos.delete("/endpoint")

    # then
    assert exc_info.value.request is not None
    assert exc_info.value.body is None
    assert "An unknown error occurred." in str(exc_info.value)


# PATCH
@responses.activate
def test_patch(modulos):
    # given
    response_patch = responses.Response(
        method="PATCH",
        url=f"{modulos.base_url}/endpoint",
        json={"key": "value"},
        status=200,
    )
    responses.add(response_patch)

    # when
    response = modulos.patch("/endpoint", data={"key": "value"})

    # then
    assert response.status_code == 200
    assert response.json() == {"key": "value"}


@responses.activate
def test_patch_http_error(modulos):
    # given

    response_patch = responses.Response(
        method="PATCH",
        url=f"{modulos.base_url}/endpoint",
        json={"key": "value"},
        status=404,
    )
    responses.add(response_patch)

    # when
    with pytest.raises(_exceptions.APIStatusError) as exc_info:
        modulos.patch("/endpoint", data={"key": "value"})

    # then
    assert exc_info.value.status_code == 404
    assert exc_info.value.request_id is None
    assert isinstance(exc_info.value.response, requests.Response)


@responses.activate
def test_patch_timeout_error(modulos):
    # given

    response_patch = responses.Response(
        method="PATCH",
        url=f"{modulos.base_url}/endpoint",
        body=requests.exceptions.ReadTimeout(),
    )
    responses.add(response_patch)

    # when
    with pytest.raises(_exceptions.APITimeoutError) as exc_info:
        modulos.patch("/endpoint", data={"key": "value"})

    # then
    assert exc_info.value.request is not None
    assert exc_info.value.body is None
    assert "Request timed out." in str(exc_info.value)


@responses.activate
def test_patch_connection_error(modulos):
    # given

    response_patch = responses.Response(
        method="PATCH",
        url=f"{modulos.base_url}/endpoint",
        body=requests.exceptions.ConnectionError(),
    )
    responses.add(response_patch)

    # when
    with pytest.raises(_exceptions.APIConnectionError) as exc_info:
        modulos.patch("/endpoint", data={"key": "value"})

    # then
    assert exc_info.value.request is not None
    assert exc_info.value.body is None
    assert "Connection error." in str(exc_info.value)


@responses.activate
def test_patch_api_error(modulos):
    # given

    response_patch = responses.Response(
        method="PATCH",
        url=f"{modulos.base_url}/endpoint",
        body=requests.exceptions.RequestException(),
    )
    responses.add(response_patch)

    # when
    with pytest.raises(_exceptions.APIError) as exc_info:
        modulos.patch("/endpoint", data={"key": "value"})

    # then
    assert exc_info.value.request is not None
    assert exc_info.value.body is None
    assert "An unknown error occurred." in str(exc_info.value)
