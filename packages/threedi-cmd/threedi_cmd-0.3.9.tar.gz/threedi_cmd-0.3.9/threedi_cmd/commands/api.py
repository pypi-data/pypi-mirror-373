import asyncio
import sys
from datetime import datetime
from pathlib import Path

import click
import typer
import websockets
from rich import box
from rich.padding import Padding
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table
from threedi_api_client.api import Configuration
from threedi_api_client.openapi.api.v3_api import V3Api
from threedi_api_client.openapi.exceptions import ApiException

from threedi_cmd.commands.callbacks import default_callback
from threedi_cmd.commands.scenarios import scenarios
from threedi_cmd.commands.utils import PathPrompt, download_files
from threedi_cmd.console import console
from threedi_cmd.errors import ExitCodes, LoadScenarioError
from threedi_cmd.logger import get_logger
from threedi_cmd.models.errors import ApiModelError
from threedi_cmd.models.scenario import FailedStep, ResolveError
from threedi_cmd.parser import ScenarioParser

logger = get_logger("INFO")

DEFAULT_PAGER_SIZE = 20


app = typer.Typer()
api_app = typer.Typer(callback=default_callback)
app.add_typer(api_app, name="api")


@api_app.command()
def models(ctx: typer.Context):
    """List available threedimodels"""
    threedi_models_api: V3Api = ctx.obj.api_client
    threedi_models = threedi_models_api.threedimodels_list()

    table = Table(
        show_header=True,
        box=box.HORIZONTALS,
        show_lines=False,
        width=(console.width * 80) / 100,
    )
    table.add_column("Id", width=5)
    table.add_column(
        "Name",
        width=20,
        justify="left",
        style="bold cyan",
        header_style="bold cyan",
    )
    table.add_column("Revision", justify="left")
    table.add_column("Inp success", justify="left")

    remaining = threedi_models.count
    limit = min(DEFAULT_PAGER_SIZE, remaining)

    while remaining == threedi_models.count or (
        remaining > 0 and Confirm.ask("Show more?")
    ):
        threedi_models = threedi_models_api.threedimodels_list(
            limit=limit, offset=remaining - limit
        )
        for i, model in enumerate(threedi_models.results):
            if model.inp_success is True:
                txt = f":heavy_check_mark: [bold green]{model.inp_success}[/bold green] "
            else:
                txt = f"[bold red]{model.inp_success}[/bold red]"
            table.add_row(f"{model.id}", f"{model.name}", f"{model.revision_hash}", txt)
        remaining -= limit
        limit = min(remaining, DEFAULT_PAGER_SIZE)
        console.print(table)


@api_app.command()
def organisations(ctx: typer.Context):
    """List available organisations"""
    organisations_api: V3Api = ctx.obj.api_client
    organisations = organisations_api.organisations_list()
    table = Table(
        show_header=True,
        box=box.HORIZONTALS,
        show_lines=False,
        width=(console.width * 80) / 100,
    )
    table.add_column("Unique Id", width=15)
    table.add_column(
        "Name",
        width=20,
        justify="left",
        style="bold cyan",
        header_style="bold cyan",
    )

    remaining = organisations.count
    limit = min(DEFAULT_PAGER_SIZE, remaining)

    while remaining == organisations.count or (
        remaining > 0 and Confirm.ask("Show more?")
    ):
        organisations = organisations_api.organisations_list(
            limit=limit, offset=remaining - limit
        )
        for i, org in enumerate(organisations.results):
            table.add_row(f"{org.unique_id}", f"{org.name}")
        remaining -= limit
        limit = min(remaining, DEFAULT_PAGER_SIZE)
        console.print(table)


@api_app.command()
def simulations(
    ctx: typer.Context,
    queued: bool = typer.Option(
        False,
        "--queued",
        help="Show the current queue",
    ),
):
    """List simulations"""
    simulations_api: V3Api = ctx.obj.api_client
    simulations = simulations_api.simulations_list()

    table = Table(
        show_header=True,
        box=box.HORIZONTALS,
        show_lines=False,
        width=(console.width * 80) / 100,
    )
    table.add_column(
        "Id", width=5
    )  # , style="dark_green", header_style="bold dark_green")
    table.add_column("Name", width=20, justify="left")
    table.add_column("Status", justify="left")

    remaining = simulations.count
    limit = DEFAULT_PAGER_SIZE
    offset = 0
    while remaining == simulations.count or (remaining > 0 and Confirm.ask("Show more?")):
        simulations = simulations_api.simulations_list(limit=limit, offset=offset)
        for i, simulation in enumerate(simulations.results):
            status = simulations_api.simulations_status_list(simulation.id)
            if status.name == "finished":
                txt = f":heavy_check_mark: [bold green]{status.name}[/bold green] "
            elif status.name == "created":
                txt = f"[dim grey27]{status.name}[/dim grey27] "
            elif status.name == "initialized":
                txt = f"[bold dark_violet]{status.name}[/bold dark_violet] "
            else:
                txt = f"[bold red]{status.name}[/bold red]"
            table.add_row(f"{simulation.id}", f"{simulation.name}", txt)
        console.print(table)
        remaining -= limit
        offset += DEFAULT_PAGER_SIZE


@api_app.command()
def settings(
    ctx: typer.Context,
    organisation: str = typer.Option(
        None, help="Unique-id of the organisation to set as default"
    ),
    scenario_folder: Path = typer.Option(
        None,
        dir_okay=True,
        writable=True,
        resolve_path=True,
        help="Specify a the folder for your scenario's.",
    ),
    result_folder: Path = typer.Option(
        None,
        dir_okay=True,
        writable=True,
        resolve_path=True,
        help="Specify a results folder.",
    ),
):
    """Set default settings"""
    console.rule(":wrench: Configuring defaults for the 3Di cli", style="bold blue")
    console.print(Padding("", (1, 0)))
    if organisation is None:
        console.rule("Please choose an organisation", style="bold blue")
        if (
            ctx.obj.organisation_uuid
            and Confirm.ask(f"Change current organisation {ctx.obj.organisation_uuid}?")
            or not ctx.obj.organisation_uuid
        ):
            organisations(ctx)
            console.rule(":pencil2:", style="bold blue")
            organisation = Prompt.ask(
                "Set default organisation. UNIQUE_ID",
                default=ctx.obj.organisation_uuid,
            )
        else:
            organisation = ctx.obj.organisation_uuid
    if not scenario_folder:
        default_scenario_path = ctx.obj.scenario_folder or Path("./scenarios").resolve()
        print(default_scenario_path)
        scenario_folder = PathPrompt.ask(
            "Where do you keep your scenario files?", default=default_scenario_path
        )
    if not result_folder:
        results_folder_default = ctx.obj.result_folder or Path("./results").resolve()
        result_folder = PathPrompt.ask(
            "Where do you want to store your result files?",
            default=results_folder_default,
        )
    ctx.obj.organisation_uuid = organisation
    ctx.obj.result_folder = result_folder
    ctx.obj.scenario_folder = scenario_folder
    console.print(
        f":heavy_check_mark: Default settings are saved in {ctx.obj.config_file}"
    )


@api_app.command()
def run_scenario(
    ctx: typer.Context,
    scenario: int = typer.Option(
        None,
        help="The ID of the scenario, as returned by the 'scenarios' command. If not provided the scenarios command will be invoked so you can choose an ID",
    ),
    model_id: int = typer.Option(
        None,
        help="The ID of the model you want to use, as returned by the 'models' command. If not provided the models command will be invoked so you can choose an ID",
    ),
    organisation: str = typer.Option(
        None, help="Unique-id of the organisation to set as default"
    ),
):
    """Run a scenario"""
    if scenario is None:
        scenarios(ctx)
        scenario = IntPrompt.ask("Which scenario do you want to run? ID")
    scenario_to_run = ctx.obj.scenarios[scenario]["file"]
    parser = ScenarioParser(scenario_to_run)

    if parser.is_simulation_scenario:
        if model_id is None:
            models(ctx)
            model_id = IntPrompt.ask("Which model do you want to run? ID")

    if not organisation:
        organisations(ctx)
        organisation = Prompt.ask("Which organisation do you want to use? UUID")

    name = ctx.obj.scenarios[scenario]["name"]

    model = ctx.obj.api_client.threedimodels_read(model_id)
    context = {
        "threedimodel_id": model.id,
        "threedimodel": model,
        "organisation_uuid": organisation,
        "simulation_name": name,
        "schematisation_name": name,
        "datetime_now": datetime.utcnow().isoformat(),
    }

    try:
        scenario = parser.parse(
            ctx.obj.api_client, ctx.obj.websocket_settings, context=context
        )
    except (ResolveError, ApiModelError, LoadScenarioError) as err:
        console.print(f":collision: {err}", style="error")
        sys.exit(ExitCodes.SCENARIO_CONFIG_ERROR.value)

    console.rule(f"Loading scenario {name}", style="bold blue")
    scenario.base_object.save()
    console.print(f":link: URL: {scenario.base_object.instance.url}")

    try:
        console.rule("Starting scenario run...", style="bold blue")
        asyncio.run(scenario.execute())
    except KeyboardInterrupt:
        pass
    except FailedStep as err:
        console.print(f"{err}", style="error")
        sys.exit(ExitCodes.RUN_SCENARIO_ERROR.value)
    except websockets.exceptions.InvalidStatusCode as err:
        console.print(f"{err}", style="error")
        sys.exit(ExitCodes.CONNECTION_ERROR.value)
    else:
        success_panel = Panel(
            f"Run for scenario {name} successful",
            expand=True,
            box=box.DOUBLE,
            border_style="bold spring_green4",
            title=":sparkles: Finished :sparkles:",
        )
        console.print(success_panel, justify="center")


@api_app.command()
def results(
    ctx: typer.Context,
    simulation: int = typer.Option(None, help="ID of the simulation"),
    folder: Path = typer.Option(
        None,
        dir_okay=True,
        writable=True,
        resolve_path=True,
        help="Absolute path to where the files will be stored.",
    ),
):
    """Download results of a simulation"""
    console.rule(":arrow_heading_down:  Download simulation results", style="bold blue")
    console.print(Padding("", (1, 0)))

    if simulation is None:
        console.rule("Please choose a simulation", style="bold blue")
        simulations(ctx)
        simulation = IntPrompt.ask("Which simulation results do you want download? ID")
    if not folder:
        result_folder = ctx.obj.result_folder
        if not result_folder:
            result_folder = Path.cwd()
        folder = PathPrompt.ask(
            "Where do you want to store the results files?",
            default=Path(f"{result_folder}/simulation-{simulation}"),
        )

    try:
        folder.resolve().mkdir(parents=True)
    except FileExistsError:
        click.confirm(
            "Output folder already exists, we might override files in the folder. "
            "Do you want to continue?",
            abort=True,
        )

    try:
        simulations_api: V3Api = ctx.obj.api_client
        threedimodels_api = simulations_api
        simulation = simulations_api.simulations_read(id=simulation)
    except ApiException as err:
        console.print(f"{err}", style="error")
        sys.exit(ExitCodes.RETRIEVE_ERROR.value)
    threedi_model_id = simulation.threedimodel_id

    gridadmin_download = threedimodels_api.threedimodels_gridadmin_download(
        threedi_model_id
    )
    f = [gridadmin_download]

    result_files = simulations_api.simulations_results_files_list(simulation.id)
    for result in result_files.results:
        if result.file.state in ["error", "removed"]:
            console.print(
                f"{result.filename} is in state {result.file.state} and will be skipped.",
                style="warning",
            )
            continue

        result_download = simulations_api.simulations_results_files_download(
            id=result.id, simulation_pk=simulation.id
        )
        f.append(result_download)
    success = download_files(f, folder)
    if success:
        console.print(":heavy_check_mark: Finished downloading results", style="success")
    else:
        console.print(":collision: Not all files could be downloaded", style="error")


@api_app.command()
def login(ctx: typer.Context):
    """Login to the specified endpoint."""
    try:
        configuration = Configuration(ctx.obj.endpoint)
        ctx.obj.credentials_prompt(configuration)
        console.print(f":unlock: Authenticated as {ctx.obj.username}", style="success")
    except ApiException as e:
        console.print(f":lock: Failed to authenticate: {e.reason}", style="warning")
        sys.exit(ExitCodes.AUTHENTICATION_FAILED.value)


if __name__ == "__main__":
    app()
