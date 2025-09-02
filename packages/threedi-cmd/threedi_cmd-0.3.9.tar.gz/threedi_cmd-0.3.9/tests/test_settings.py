from pathlib import Path
from unittest.mock import patch

import pytest
from threedi_api_client.openapi import Configuration

from threedi_cmd.commands.settings import CachedConfig, EndpointOption, Settings


@pytest.fixture
def configuration():
    conf = Configuration(
        host="test",
        username="tester",
        api_key={
            "Authorization": "",
            "refresh": "",
        },
        api_key_prefix={"Authorization": "Bearer"},
    )
    return conf


@pytest.fixture
def config_file(tmp_path, cache_content) -> Path:
    c = CachedConfig(**cache_content)
    f = tmp_path / "test_config.yaml"
    c.save_to_file(f)
    yield f


@pytest.fixture
def settings_instance(monkeypatch, configuration, config_file):
    def mock_credentials_prompt(*args, **kwargs):
        return None

    monkeypatch.setattr(Settings, "configuration", configuration)
    monkeypatch.setattr(Settings, "credentials_prompt", mock_credentials_prompt)
    monkeypatch.setattr(Settings, "config_file", config_file)
    yield Settings("localhost")


def test_settings(settings_instance):
    assert settings_instance.username == "test"
    assert (
        settings_instance.access
        == "eyJ0eXAiOiJKV1XPOCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjEyNTM3OTk1LCJqdGkiOiI1ZjFlYjQ4ZTU2MTY0OTIzYjk5NzNlYWE3MTZmMDJiMyIsInVzZXJfaWQiOiJyb290In0.OlA9G9_ZIyoK8NViEDEoLFQxqwxLjwmzrio7wAgZHrs"
    )
    assert settings_instance.organisation_uuid == "8df668f217494cdfaff89c1a731f31cb"
    assert settings_instance.endpoint == EndpointOption.localhost.value


def test_set_settings_properties(settings_instance):
    assert settings_instance.username == "test"
    settings_instance.username = "the.great.pretender"
    assert settings_instance.username == "the.great.pretender"
    assert settings_instance.cached_config.username == "the.great.pretender"


def test_save_settigns(config_file, settings_instance):
    assert config_file.exists() and config_file.is_file()
    config_file.unlink()
    assert not config_file.exists()
    settings_instance.save()
    assert config_file.exists() and config_file.is_file()


@patch.object(Settings, "save", side_effect=IOError)
def test_save_settigns_error(config_file, settings_instance):
    with pytest.raises(IOError):
        settings_instance.save()
