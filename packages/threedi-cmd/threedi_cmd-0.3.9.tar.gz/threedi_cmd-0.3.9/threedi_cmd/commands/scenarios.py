import typer
from rich import box
from rich.table import Table

from threedi_cmd.commands.callbacks import default_callback
from threedi_cmd.commands.settings import (
    ScenariosMeta,
)
from threedi_cmd.console import console
from threedi_cmd.logger import get_logger

logger = get_logger("INFO")

DEFAULT_PAGER_SIZE = 20


scenario_app = typer.Typer(callback=default_callback)


@scenario_app.command()
def scenarios(ctx: typer.Context):
    """List local scenarios"""
    table = Table(show_header=True, box=box.HORIZONTALS, show_lines=True)
    table.add_column("Id", width=5)
    table.add_column(
        "Name",
        width=20,
        justify="left",
        style="bold cyan",
        header_style="bold cyan",
    )
    table.add_column("Description", justify="left", no_wrap=False)
    table.add_column(
        "Caution", justify="left", style="orange3", header_style="bold orange3"
    )
    table.add_column("yaml", justify="left", style="dim blue", header_style="bold blue")
    s = ScenariosMeta(ctx.obj.scenario_folder)
    for i, scenario in enumerate(s.scenarios, start=0):
        if isinstance(scenario, dict):
            s = ""
            if scenario.get("known_constraints"):
                for k, v in scenario["known_constraints"].items():
                    s += f"{k}: {v} \n"
            table.add_row(
                f"{i}",
                f"{scenario['name']}",
                f"{scenario['description']}",
                f"{s}",
                f"{scenario['file'].stem}",
            )
    console.print(table)


if __name__ == "__main__":
    scenario_app()
