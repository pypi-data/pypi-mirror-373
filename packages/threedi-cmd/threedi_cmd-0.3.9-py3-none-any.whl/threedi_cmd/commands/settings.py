from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import List
from urllib.parse import urlparse

import click
import yaml
from rich.prompt import Prompt
from threedi_api_client.aio.threedi_api_client import (
    ThreediApiClient as AsyncThreediApiClient,
)
from threedi_api_client.api import ThreediApi
from threedi_api_client.openapi.exceptions import ApiException
from threedi_api_client.threedi_api_client import Configuration, ThreediApiClient

try:
    from threedi_api_client.auth import get_auth_token, is_token_usable, refresh_api_key
except ImportError:
    from threedi_api_client.threedi_api_client import (
        get_auth_token,
        is_token_usable,
        refresh_api_key,
    )

from threedi_cmd.console import console
from threedi_cmd.errors import ExitCodes

SCENARIO_DIR = Path(__file__).parent.parent / "scenarios"


class EndpointOption(Enum):
    localhost = "http://localhost:8000"
    staging = "https://api.staging.3di.live"
    production = "https://api.3di.live"


@lru_cache()
def get_settings(endpoint):
    return Settings(endpoint=endpoint)


@dataclass
class WebSocketSettings:
    api_base_url: str
    token: str
    host: str = field(init=False)
    proto: str = field(init=False)
    api_version: str = field(init=False)

    def __post_init__(self):
        parsed_url = urlparse(self.api_base_url)
        self.host = parsed_url.netloc
        self.proto = "wss" if parsed_url.scheme == "https" else "ws"
        self.api_version = parsed_url.path.lstrip("/")
        self.token = (
            self.token if self.token.startswith("Bearer") else f"Bearer {self.token}"
        )


@dataclass
class CachedConfig:
    username: str = ""
    access: str = ""
    refresh: str = ""
    organisation_uuid: str = ""
    result_folder: str = ""
    scenario_folder: str = ""

    @classmethod
    def load_from_file(cls, file: Path) -> CachedConfig:
        """
        Loads saved settings from 3di_config.yaml. See save method for available attributes.
        """
        try:
            with open(file, "r") as f:
                cached_data = yaml.load(f, Loader=yaml.FullLoader)
                return cls(**cached_data)
        except OSError:
            # settings file does not yet exist
            return cls()

    def save_to_file(self, file: Path) -> None:
        with open(file, "w") as f:
            yaml.dump(
                asdict(self),
                default_flow_style=False,
                stream=f,
            )


@dataclass
class ScenariosMeta:
    scenario_dir: Path = SCENARIO_DIR

    @property
    def scenarios(self) -> List:
        scenario_list = []
        scenario_files = self.scenario_dir.glob("*.yaml")
        for f in scenario_files:
            with f.open("r") as y:
                content = yaml.load_all(y, Loader=yaml.FullLoader)
                try:
                    meta = next(content)["meta"]
                    meta["file"] = f
                    scenario_list.append(meta)
                except KeyError:
                    raise AttributeError(
                        "The scenario definition is missing the 'meta' section"
                    )
        return scenario_list


class Settings:
    """Settings that are saved (authentication) values between calls to the cli.

    The default settings are saved in the file '3di_config.yaml' which lives in
    the configuration folder of your operating system.
    """

    APP_NAME = "3di-scenario"
    CONFIG_FILE_NAME = "3di_config.yaml"

    def __init__(self, endpoint: str = "", websocket_api_version="v3-beta"):
        self._endpoint = EndpointOption[endpoint]
        self.cached_config = CachedConfig.load_from_file(self.config_file)

        if not is_token_usable(self.access):
            self.credentials_prompt(self.configuration)

        self.websocket_settings = WebSocketSettings(
            api_base_url=self.endpoint + "/" + websocket_api_version, token=self.access
        )

    @property
    def endpoint(self) -> str:
        return self._endpoint.value

    @property
    def username(self) -> str:
        # print(f"prop username {self._username}")
        return self.cached_config.username

    @username.setter
    def username(self, username: str):
        self.cached_config.username = username

    @property
    def access(self) -> str:
        return self.cached_config.access

    @access.setter
    def access(self, access: str):
        self.cached_config.access = access

    @property
    def refresh(self) -> str:
        return self.cached_config.refresh

    @refresh.setter
    def refresh(self, refresh: str):
        self.cached_config.refresh = refresh

    @property
    def organisation_uuid(self) -> str:
        return self.cached_config.organisation_uuid

    @organisation_uuid.setter
    def organisation_uuid(self, organisation_uuid: str):
        self.cached_config.organisation_uuid = organisation_uuid

    @property
    def result_folder(self) -> Path:
        return Path(self.cached_config.result_folder).resolve()

    @result_folder.setter
    def result_folder(self, result_folder: Path):
        if isinstance(result_folder, Path):
            result_folder = result_folder.resolve().as_posix()
        self.cached_config.result_folder = result_folder

    @property
    def scenario_folder(self) -> Path:
        return Path(self.cached_config.scenario_folder).resolve()

    @scenario_folder.setter
    def scenario_folder(self, scenario_folder: Path):
        if isinstance(scenario_folder, Path):
            scenario_folder = scenario_folder.resolve().as_posix()
        self.cached_config.scenario_folder = scenario_folder

    @property
    def app_dir(self) -> Path:
        _app_dir = Path(click.get_app_dir(app_name=self.APP_NAME))
        _app_dir.mkdir(parents=True, exist_ok=True)
        return _app_dir

    @property
    def config_file(self) -> Path:
        return self.app_dir / f"{self._endpoint.name}_{self.CONFIG_FILE_NAME}"

    @property
    def configuration(self) -> Configuration:
        configuration = Configuration(
            host=self.endpoint,
            username=f"{self.username}",
            api_key={
                "Authorization": f"{self.access}",
                "refresh": f"{self.refresh}",
            },
            api_key_prefix={"Authorization": "Bearer"},
        )
        configuration.refresh_api_key_hook = refresh_api_key
        if not self.username:
            self.credentials_prompt(configuration)
        return configuration

    @property
    def api_client(self) -> ThreediApiClient:
        client = ThreediApi(
            config={
                "THREEDI_API_HOST": self.endpoint,
                "THREEDI_API_USERNAME": self.username,
                "THREEDI_API_ACCESS_TOKEN": self.access,
                "THREEDI_API_REFRESH_TOKEN": self.refresh,
            },
            version="v3-beta",
        )
        return client

    @property
    def async_api_client(self) -> AsyncThreediApiClient:
        client = AsyncThreediApiClient(self.configuration)
        return client

    @property
    def scenarios(self) -> List:
        scenarios_meta = ScenariosMeta(self.scenario_folder)
        return scenarios_meta.scenarios

    def save(self) -> None:
        try:
            self.cached_config.save_to_file(self.config_file)
        except IOError as err:
            console.print(
                f"Saving cache to {self.config_file} failed with: {err}", style="error"
            )
            return

    @staticmethod
    def save_settings() -> None:
        ctx = click.get_current_context()
        ctx.obj.save()

    def credentials_prompt(self, config: Configuration) -> None:
        console.rule(
            f":key: Authentication required for {config.host}",
            characters="*",
            style="gold3",
        )
        kwargs = {}
        try:
            if self.username:
                kwargs.update({"default": self.username})
        except AttributeError:
            pass
        username = Prompt.ask("Username", **kwargs)
        password = Prompt.ask("Password", password=True)

        try:
            token = get_auth_token(username, password, config.host)
        except ValueError as err:
            console.print(f":collision: {err}", style="error")
            sys.exit(ExitCodes.AUTHENTICATION_FAILED.value)
        except ApiException as err:
            body = json.loads(err.body)["detail"]
            console.print(
                f"Could not log you in. The server responded with: {body}",
                style="error",
            )
            sys.exit(ExitCodes.AUTHENTICATION_FAILED.value)

        # Update the settings
        self.username = username
        self.password = password
        self.access = token["access"]
        self.refresh = token["refresh"]
        config.api_key = {"Authorization": self.access, "refresh": self.refresh}
