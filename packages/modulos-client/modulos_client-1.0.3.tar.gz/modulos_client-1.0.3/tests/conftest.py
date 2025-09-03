import tempfile
import pytest
import yaml


@pytest.fixture
def config_file():
    config = {
        "active_profile": "Peter",
        "profiles": {
            "Peter": {"host": "http://localhost", "name": "Peter", "token": "my_token"}
        },
    }
    with tempfile.NamedTemporaryFile() as f:
        with open(f.name, "w") as f:
            yaml.dump(config, f)
        yield f.name


@pytest.fixture
def config_file_two_profiles():
    config = {
        "active_profile": "Peter",
        "profiles": {
            "Peter": {"host": "http://localhost", "name": "Peter", "token": "my_token"},
            "Pan": {"host": "http://localhost", "name": "Pan", "token": "other_token"},
        },
    }
    with tempfile.NamedTemporaryFile() as f:
        with open(f.name, "w") as f:
            yaml.dump(config, f)
        yield f.name


@pytest.fixture
def modulos():
    from modulos_client import Modulos

    return Modulos(api_key="your_api_key", base_url="https://dev.modulos.ai/api")
