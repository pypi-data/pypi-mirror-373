import asyncio
from datetime import datetime

import typer

from threedi_cmd.commands.callbacks import default_callback
from threedi_cmd.console import console
from threedi_cmd.models.monitor import ActiveSimulations

active_sims_app = typer.Typer(callback=default_callback)


async def monitor_active_simulations(endpoint: str) -> None:
    """
    executes ActiveSimlations "run_monitor" task in the background
    """
    active_simulations = ActiveSimulations(endpoint)
    result = await asyncio.gather(
        active_simulations.run_monitor(), return_exceptions=True
    )
    if result:
        console.print(result, style="error")


@active_sims_app.command()
def simulations(ctx: typer.Context):
    """
    Show currently running simulations
    """
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        console.print(f"[{start_time}] Starting active simulations worker")
        asyncio.run(monitor_active_simulations(ctx.obj._endpoint.name))
    except KeyboardInterrupt:
        pass
    finally:
        console.print(
            ":sparkles: Bye bye, hope to see you soon! :sparkles:",
            style="success",
        )


if __name__ == "__main__":
    active_sims_app()
