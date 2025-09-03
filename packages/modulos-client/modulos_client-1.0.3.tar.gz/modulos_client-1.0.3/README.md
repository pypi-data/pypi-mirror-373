# Modulos Client

[![PyPI version](https://img.shields.io/pypi/v/modulos-client.svg)](https://pypi.org/project/modulos-client/)

This tool provides a Programmatic interface to interact with the Modulos platform.

## Documentation

The documentation can be found on [docs.modulos.ai](https://docs.modulos.ai)

## Installation

```sh
# install from PyPI
pip install modulos-client
```

## API Key

Generate your API key [here](https://app.modulos.ai/tokens)

## Usage

```python
import os
from modulos_client import Modulos

client = Modulos(
    # This is the default and can be omitted
    api_key=os.environ.get("MODULOS_API_KEY"),
)
```

While you can provide an `api_key` keyword argument,
we recommend using [python-dotenv](https://pypi.org/project/python-dotenv/)
to add `MODULOS_API_KEY="My API Key"` to your `.env` file
so that your API Key is not stored in source control.

## Handling errors

When the library is unable to connect to the API (for example, due to network connection problems or a timeout), a subclass of `modulos_client.APIConnectionError` is raised.

When the API returns a non-success status code (that is, 4xx or 5xx
response), a subclass of `modulos_client.APIStatusError` is raised, containing `status_code` and `response` properties.

All errors inherit from `modulos_client.APIError`.

```python
import modulos_client
from modulos_client import Modulos

client = Modulos()

try:
    metrics = client.testing.logs.get_metrics(project_id)
except modulos_client.APIConnectionError as e:
    print("The server could not be reached")
    print(e.__cause__)  # an underlying Exception, likely raised within httpx.
except modulos_client.APIStatusError as e:
    print("Another non-200-range status code was received")
    print(e.status_code)
    print(e.response)
```

Error codes are as followed:

| Status Code | Error Type                 |
| ----------- | -------------------------- |
| 400         | `BadRequestError`          |
| 401         | `AuthenticationError`      |
| 403         | `PermissionDeniedError`    |
| 404         | `NotFoundError`            |
| 422         | `UnprocessableEntityError` |
| >=500       | `InternalServerError`      |
| N/A         | `APIConnectionError`       |
