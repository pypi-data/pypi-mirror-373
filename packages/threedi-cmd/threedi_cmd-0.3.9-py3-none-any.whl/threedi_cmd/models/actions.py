import logging
from time import sleep

from rich.live import Live
from threedi_api_client.openapi.exceptions import ApiException
from threedi_api_client.openapi.models import Action

from threedi_cmd.console import console
from threedi_cmd.logger import log_settings

from .base import SimulationChildWrapper
from .waitfor import WaitForStatusWrapper, WaitForTimeWrapper

logger = logging.getLogger(__name__)

MAX_RETRIES = 10


class ActionWrapper(SimulationChildWrapper):
    model = Action
    api_path: str = "actions"
    scenario_name = model.__name__.lower()

    def create(self, retry_count: int = 0):
        """Try to create the action, retrying if no more sessions are available"""
        if retry_count > MAX_RETRIES:
            raise Exception("Failed to execute simulation create action after 10 retries")

        try:
            if log_settings.get("use_rich_logging", False):
                with Live(console=console) as live:
                    live.update(f"Creating {self.model.__name__}...")
                    func = getattr(self.api, f"{self.base_path}{self.api_path}_create")

                    data = self.instance.to_dict()
                    data = {key: item for key, item in data.items() if item is not None}

                    res = func(self.simulation.id, data)
                    live.update(
                        f":heavy_check_mark: [bold spring_green4] Created {self.model.__name__}"
                    )
            else:
                func = getattr(self.api, f"{self.base_path}{self.api_path}_create")
                res = func(self.simulation.id, self.instance)
        except ApiException as e:
            if (
                e.status == 429
                and e.body is not None
                and "has no more sessions available" in e.body
            ):
                retry_count += 1
                sleep_time = retry_count**2
                logger.info(
                    f"No more sessions available, retrying... (waiting {sleep_time} seconds)"
                )
                sleep(sleep_time)
                return self.create(retry_count)

            raise e

        console.print(self._data)
        return res

    @property
    def extra_steps(self):
        extra_steps = []
        name = self.instance.name
        if name == "initialize":
            data = {"name": "initialized", "paused": True}
        elif name == "start":
            data = {"name": "initialized", "paused": False}
        elif name == "pause":
            data = {"name": "initialized", "paused": True}
        elif name == "shutdown":
            data = {"name": "finished"}
        elif name == "queue":
            msg = "'queue' step is not yet implemented"
            raise NotImplementedError(msg)
        else:
            msg = f"Unknown name {name}"
            raise ValueError(msg)

        extra = {}
        if "waitfor_timeout" in self._data:
            extra["timeout"] = self._data["waitfor_timeout"]

        wait_for_status = WaitForStatusWrapper(
            data={**data, **extra},
            api_client=self._api_client,
            simulation=self.simulation,
        )
        extra_steps.append(wait_for_status)

        if self.instance.duration is not None:
            extra_steps.append(
                WaitForStatusWrapper(
                    data={"name": "initialized", "paused": True, **extra},
                    api_client=self._api_client,
                    simulation=self.simulation,
                )
            )
            extra_steps.append(
                WaitForTimeWrapper(
                    data={"time": self.instance.duration, **extra},
                    api_client=self._api_client,
                    simulation=self.simulation,
                )
            )
        return extra_steps
