import typer

from threedi_cmd.commands.active_simulations import active_sims_app
from threedi_cmd.commands.api import api_app
from threedi_cmd.commands.scenarios import scenario_app
from threedi_cmd.commands.suite import suite_app
from threedi_cmd.plugins.models import AppMeta, AppRegistry

core = typer.Typer()

# main app definition
core = AppMeta(app=core, name="core", help="Interact with various parts of 3Di")

live = AppMeta(
    app=active_sims_app,
    name="live",
    help="Get real time updates of running simulations",
    add_to="core",
)

scenarios = AppMeta(
    app=scenario_app,
    name="scenarios",
    help="Manage your local scenarios",
    add_to="core",
)

api = AppMeta(
    app=api_app, name="api", help="Interact with with the 3Di API", add_to="core"
)

suite = AppMeta(app=suite_app, name="suite", help="Run a scenario suite", add_to="core")

registry = AppRegistry(apps={inst.name: inst for inst in [core, live, scenarios, api]})
