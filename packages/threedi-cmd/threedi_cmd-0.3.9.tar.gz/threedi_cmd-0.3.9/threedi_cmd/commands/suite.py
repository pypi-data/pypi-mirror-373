import asyncio
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List

import typer
import yaml
from rich import box
from rich.padding import Padding
from rich.table import Table
from threedi_api_client.api import ThreediApi
from threedi_api_client.openapi.api import V3Api
from threedi_api_client.openapi.models import ThreediModel

from threedi_cmd.commands.settings import WebSocketSettings
from threedi_cmd.commands.slack_notify import SlackNotifier
from threedi_cmd.console import console
from threedi_cmd.errors import ExitCodes, LoadCredentialsError, LoadSuiteError
from threedi_cmd.models.scenario import FailedStep, Scenario
from threedi_cmd.parser import ScenarioParser

suite_app = typer.Typer()


class SuiteError(BaseException):
    pass


@dataclass
class SlackNotify:
    channel: str
    crashes: bool = True
    all_success: bool = True


@dataclass
class User:
    username: str
    password: str

    def __repr__(self):
        return f"User(username='{self.username}', password='********')"


@dataclass
class Credentials:
    users: List[User]
    slack_token: str = None

    @classmethod
    def load_from_file(cls, file: Path = None):
        try:
            with file.open("r") as f:
                data = yaml.load(f, Loader=yaml.FullLoader) or {}
        except OSError:
            # settings file does not yet exist
            msg = f"Could not load credentials: {file}"
            raise LoadCredentialsError(msg)
        data["credentials"]["users"] = [
            User(**x) for x in data["credentials"].get("users", [])
        ]
        return Credentials(**data["credentials"])

    def get_user(self, username: str):
        found = [x for x in self.users if x.username == username]
        assert (
            len(found) == 1
        ), f"Did not find exactly one user for {username} in the credentials"

        return found[0]


@dataclass
class SuiteScenario:
    name: str
    scenario: Scenario
    finished: bool = False
    success: bool = False
    reason: str = "scenario is not finished"
    simulation_id = None


@dataclass
class Report:
    endpoint: str
    scenarios: List[SuiteScenario]

    def simulation_url(self, suite_scenario, api_version="v3-beta"):
        return (
            f"<{self.endpoint}/{api_version}/simulations/"
            + f"{suite_scenario.simulation_id}|{suite_scenario.simulation_id}>"
        )

    @property
    def title(self):
        return f"Results framework suite run on {self.endpoint}"

    def get_slack_report(self):
        report_lines = [f"{self.endpoint}:"]
        for suite_scenario in self.scenarios:
            if suite_scenario.success:
                report_lines.append(
                    f':heavy_check_mark:   "{suite_scenario.name}" '
                    f"({self.simulation_url(suite_scenario)})"
                )
            else:
                report_lines.append(
                    f':x:   "{suite_scenario.name} "'
                    f"({self.simulation_url(suite_scenario)})"
                    f" errored "
                    f"due to: {suite_scenario.reason} "
                )
        return report_lines

    def print_console_report(self, api_version="v3-beta"):
        console.print(Padding("", (1, 0)))
        console.rule(self.title, characters="•", style="black")
        console.print(Padding("", (1, 0)))
        grid = Table(
            show_header=True,
            box=box.SIMPLE,
            show_lines=False,
            width=console.width,
        )
        grid.add_column("Name")
        grid.add_column("URL", justify="left")
        grid.add_column("Details", justify="left")
        grid.add_column("Status", justify="right")
        for suite_scenario in self.scenarios:
            if suite_scenario.success:
                grid.add_row(
                    f"{suite_scenario.name}",
                    f"{self.endpoint}/{api_version}/simulations/{suite_scenario.simulation_id}",
                    "",
                    "[bold magenta]COMPLETED [green]:heavy_check_mark:",
                )
            else:
                grid.add_row(
                    f"{suite_scenario.name}",
                    f"{self.endpoint}/{api_version}/simulations/{suite_scenario.simulation_id}",
                    f"[bold gold3]{suite_scenario.reason}",
                    "[bold magenta]FAILED [red] :x:",
                )
        console.print(grid)


@dataclass
class Suite:
    endpoint: str
    path: str
    credentials: Credentials
    organisation_uuid: str
    # override_sessions: bool
    # sessions: int
    scenarios: List[SuiteScenario]
    user: str = None
    slack_notify: SlackNotify = None
    _resolved_models = None
    report: Report = field(init=False)

    def __post_init__(self):
        self.report = Report(endpoint=self.endpoint, scenarios=self.scenarios)

    @classmethod
    def resolve_model(
        cls, scenario_name, model_api, values, resolved_models
    ) -> ThreediModel:
        model = None

        if "threedimodel_filter" in values:
            cache_key = json.dumps(values["threedimodel_filter"])

            if cache_key in resolved_models:
                model = resolved_models[cache_key]
            else:
                res = model_api.threedimodels_list(
                    inp_success=True,
                    disabled=False,
                    **values["threedimodel_filter"],
                )
                if res.count == 0:
                    print(f"Error: no models found for scenario: {scenario_name}")
                    return None

                if res.count > 0:
                    console.print(
                        f"! multiple models found for lookup: {values['threedimodel_filter']}",
                        style="warning",
                    )
                model = res.results[0]
                resolved_models[cache_key] = model
        elif "threedimodel_id" in values:
            model = model_api.threedimodels_read(values["threedimodel_id"])
        else:
            print(f"No model defined for scenario: {scenario_name}")
        return model

    @classmethod
    def load_from_file(cls, file: Path = None):
        """
        :raises LoadCredentialsError if the credentials file could not be found or loaded
        :raises TypeError if the `file` argument is not of type `Path`
        :raises LoadSuiteError if the suite could not be loaded
        """
        console.rule(f"Loading suite {file.stem}", style="bold blue")

        if not isinstance(file, Path):
            raise TypeError(f"{file} must be of type pathlib.Path")
        try:
            with open(file, "r") as f:
                data = yaml.load(f, Loader=yaml.FullLoader) or {}
        except OSError:
            msg = f"Could not load suite: {file}"
            raise LoadSuiteError(msg)
        suite = data["suite"]
        base_path = file.parent

        if "slack_notify" in suite:
            suite["slack_notify"] = SlackNotify(**suite["slack_notify"])
            console.print(
                f"Suite results will be published in slack channel {suite['slack_notify'].channel}"
            )
        if "credentials" in suite:
            suite["credentials"] = Credentials.load_from_file(
                base_path / Path(suite["credentials"])
            )
        else:
            msg = "Could not find/load credentials file"
            raise LoadCredentialsError(msg)

        resolved_models = {}

        user_clients = {}

        scenarios = []
        for scenario in suite.get("scenarios", []):
            for key, values in scenario.items():
                user = values.get("user", suite.get("user", None))

                if user is None:
                    if len(suite["credentials"].users) != 1:
                        msg = "No default user specified and multiple user options in credentials"
                        raise LoadCredentialsError(msg)
                    user = suite["credentials"].users[0]
                else:
                    user = suite["credentials"].get_user(user)

                # Re-use clients
                if user.username not in user_clients:
                    config = {
                        "THREEDI_API_HOST": suite["endpoint"],
                        "THREEDI_API_USERNAME": user.username,
                        "THREEDI_API_PASSWORD": user.password,
                    }
                    user_clients[user.username] = ThreediApi(
                        config=config, version="v3-beta"
                    )

                client: V3Api = user_clients[user.username]
                token = client.api_client.configuration.get_api_key_with_prefix(
                    "Authorization"
                )

                model = cls.resolve_model(key, client, values, resolved_models)

                # Try scenario.organisation__uuid, else suite organisation_uuid
                organisation_uuid = values.get(
                    "organisation_uuid", suite["organisation_uuid"]
                )

                context = {
                    "threedimodel_id": model.id,
                    "threedimodel": model,
                    "organisation_uuid": organisation_uuid,
                    "simulation_name": key,
                    "datetime_now": datetime.utcnow().isoformat(),
                }

                scenario_to_run = base_path / Path(values["file"])
                websocket_settings = WebSocketSettings(
                    api_base_url=suite["endpoint"] + "/v3-beta", token=token
                )
                if model is not None:
                    parser = ScenarioParser(scenario_to_run)
                    scenario = parser.parse(
                        client, websocket_settings, base_path=base_path, context=context
                    )
                else:
                    scenario = None

                suite_scenario = SuiteScenario(name=key, scenario=scenario)

                if model is None:
                    suite_scenario.success = False
                    suite_scenario.reason = "could not find the model"
                    suite_scenario.finished = True

                scenarios.append(suite_scenario)
        suite["scenarios"] = scenarios
        suite["path"] = base_path
        return Suite(**suite)


async def main(suite: Path):
    """runs the entire suite"""

    try:
        suite = Suite.load_from_file(suite)
    except (TypeError, LoadCredentialsError, LoadSuiteError) as err:
        console.print(err, style="error")
        sys.exit(ExitCodes.LOADING_SUITE_ERROR.value)

    for suite_scenario in suite.scenarios:
        if suite_scenario.finished:
            continue
        console.rule("Loading scenario...", style="bold blue")
        scenario = suite_scenario.scenario
        scenario.simulation.save()

        simulation_id = scenario.simulation.instance.id
        suite_scenario.simulation_id = simulation_id
        console.rule("Starting scenario run...", style="bold blue")
        try:
            await scenario.execute()
            suite_scenario.success = True
            suite_scenario.finished = True
            console.print(
                ":sparkles: Successfully finished scenario run :sparkles:",
                style="success",
            )
        except KeyboardInterrupt:
            pass
        except FailedStep as e:
            console.print(":collision: Error running sim: {str(e)}", style="error")
            suite_scenario.success = False
            suite_scenario.finished = True
            suite_scenario.reason = str(e)
        except Exception as e:
            console.print(":collision: Error running sim: {str(e)}", style="error")
            suite_scenario.success = False
            suite_scenario.finished = True
            suite_scenario.reason = str(e)

    # Print report
    suite.report.print_console_report()
    if suite.slack_notify:
        notifier = SlackNotifier(suite.credentials.slack_token)
        notifier.send_message(
            "\n".join(suite.report.get_slack_report()),
            channel=suite.slack_notify.channel,
        )


@suite_app.command()
def run(
    suite: Path = typer.Option(
        None,
        dir_okay=True,
        writable=False,
        resolve_path=True,
        help="Specify a suite.",
    ),
):
    """Run a given suite."""
    asyncio.run(main(suite))


if __name__ == "__main__":
    suite_app()
