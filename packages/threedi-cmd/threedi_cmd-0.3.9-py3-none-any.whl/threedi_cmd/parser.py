from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from uuid import uuid4

import yaml
from jinja2 import Environment
from threedi_api_client.openapi.api.v3_beta_api import V3BetaApi
from threedi_api_client.openapi.configuration import Configuration

from threedi_cmd.websockets.settings import WebSocketSettings

from .models import WRAPPERS
from .models.scenario import (
    Scenario,
    SchematisationScenario,
    SimulationScenario,
)


def get_websocket_token_from_configuration(configuration: Configuration) -> str:
    if configuration.username == "__key__":
        # Personal API key (Basic auth)
        return configuration.get_basic_auth_token()
    # Local user with username/password (Bearer token)
    return configuration.get_api_key_with_prefix("Authorization")


class ScenarioParser:
    """
    Parses a YAML file into a Scenario object
    """

    _simulation_scenario = None
    _data = None

    def __init__(self, filepath: str):
        """
        :param filepath: The filepath to the YAML file
        :param context: The context to use for rendering the YAML (Jinja2) file
        """
        self.filepath = Path(filepath)

    def load(self):
        if self._data is None:
            with open(self.filepath.as_posix()) as f:
                self._data = f.read()
        return self._data

    def _render_template(self, context: Dict) -> str:
        """
        Render the template using the given context
        """
        # Inject default params
        context.update(
            {
                "simulation_name": "run_" + uuid4().hex,
                "schematisation_name": "schematisation_" + uuid4().hex,
                "datetime_now": datetime.utcnow().isoformat(),
            }
        )
        data = self.load()

        env = Environment(extensions=["threedi_cmd.jinja2_time.TimeExtension"])
        env.datetime_format = "%Y-%m-%dT%H:%M:%S"
        return yaml.load(env.from_string(data).render(context), Loader=yaml.FullLoader)

    @property
    def is_simulation_scenario(self):
        if self._simulation_scenario is None:
            data = yaml.load(self.load(), Loader=yaml.FullLoader)
            self._simulation_scenario = (
                "schematisation" not in data.get("scenario", {}).keys()
            )
        return self._simulation_scenario

    def parse(
        self,
        threedi_api_client: V3BetaApi,
        base_path: Optional[Path] = None,
        context: Dict = None,
    ) -> Scenario:
        """
        Parse the YAML file.

        :param threedi_api_client: Injected into the Scenario,
                                   allowing to execute API calls.

        :returns: Scenario instance
        """
        if context is None:
            context = {}

        data = self._render_template(context)
        websocket_settings = WebSocketSettings(
            api_base_url=threedi_api_client.api_client.configuration.host + "/v3-beta",
            token=get_websocket_token_from_configuration(
                threedi_api_client.api_client.configuration
            ),
        )

        scenario_klass = SimulationScenario
        if not self.is_simulation_scenario:
            scenario_klass = SchematisationScenario

        return scenario_klass(
            data=data,
            threedi_api_client=threedi_api_client,
            wrappers=WRAPPERS,
            websocket_settings=websocket_settings,
            base_path=base_path,
            context=context,
        )
