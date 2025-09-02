import asyncio
from asyncio import Queue
from dataclasses import dataclass
from time import time
from typing import Dict

from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
)
from threedi_api_client.openapi.api.v3_api import V3Api
from threedi_api_client.openapi.models import SimulationStatus

from threedi_cmd.console import console
from threedi_cmd.logger import Dummy, log_settings
from threedi_cmd.models.base import SimulationChildWrapper, class_repr, evaluate_lazy

DEFAULT_TIMEOUT = 30


class WaitForTimeout(Exception):
    pass


def match(websocket_instance, data: Dict):
    """
    Recursively try to match a dict with the websocket_instance
    (openapi model instance)
    """
    if websocket_instance is None:
        return True

    mismatch = False

    for key, value in data.items():
        if isinstance(value, dict):
            mismatch = match(getattr(websocket_instance, key, None), value)
        else:
            # Support both object and dict lookups
            if isinstance(websocket_instance, dict):
                val = websocket_instance.get(key, None)
            else:
                val = getattr(websocket_instance, key, None)
            # Allow lazy evaluation of lambda functions
            if val != evaluate_lazy(value):
                mismatch = True
        if mismatch:
            break
    return mismatch


class WaitForBase(SimulationChildWrapper):
    model = None  # Override this
    scenario_name: str = ""  # Override this
    websocket_event_type = ""  # Override this

    def __init__(self, data: Dict, api_client: V3Api, **kwargs):
        """Set the timeout to -1 to wait infinitely for the event"""
        if "timeout" in data:
            self.timeout = data.pop("timeout")
        else:
            self.timeout = DEFAULT_TIMEOUT
        super().__init__(data, api_client, **kwargs)

    def get_instance(self, data: Dict):
        instance = None
        event_type = data.get("type", None)
        event_data = data.get("data", {})

        if event_type == self.websocket_event_type:
            kwargs = {}
            for key, value in event_data.items():
                if key in self.model.openapi_types.keys():
                    kwargs[key] = value
            instance = self.model(**kwargs)
        return instance

    def matches(self, websocket_instance) -> bool:
        mismatch = match(websocket_instance, self._data)
        return not mismatch

    async def execute(self, queue: Queue, steps: list):
        description = class_repr(self._data, self.model)
        console.rule(f"[bold] Waiting for {description}", style="gold3")

        if log_settings.get("use_rich_logging", False):
            progress = Progress(
                TextColumn("[bold blue]Waiting for step to complete...", justify="right"),
                BarColumn(bar_width=25),
                TextColumn("Timeout: {task.fields[timeout]}"),
                "/",
                "{task.fields[remaining]} secs",
                "•",
                "current t: {task.fields[t]}",
            )
        else:
            progress = Dummy()

        start = time()
        if self.timeout == -1:
            remaining_time = None
        else:
            remaining_time = float(self.timeout)

        waiting = True
        sim_time = 0
        with progress:
            task = progress.add_task(
                "busy",
                total=1,
                start=False,
                timeout=self.timeout,
                remaining=remaining_time,
                t="",
            )
            while waiting:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=remaining_time)
                    try:
                        sim_time = data["sim_time"]
                    except (KeyError, TypeError):
                        pass
                    progress.update(task, remaining=int(remaining_time), t=sim_time)
                except asyncio.TimeoutError:
                    raise WaitForTimeout(f"Timeout error for: {description}")
                instance = self.get_instance(data)
                if instance is not None:
                    if self.matches(instance):
                        progress.start_task(task)
                        progress.update(task, advance=1)
                        waiting = False

                if data.get("type") == "websocket" and data.get("status") == "closing":
                    raise WaitForTimeout(data.get("reason"))

                if waiting and remaining_time is not None:
                    remaining_time = float(self.timeout) - (time() - start)
                    if remaining_time <= 0:
                        raise WaitForTimeout(f"Timeout error for: {description}")
        console.print(f":heavy_check_mark: Received {self}!")
        console.print("• Resuming scenario...")
        return instance

    def __repr__(self):
        return class_repr(self._data, self.model)


class WaitForModel(WaitForBase):
    websocket_event_type = "event"

    def get_instance(self, data: Dict):
        instance = None
        event_type = data.get("type", None)

        if event_type == self.websocket_event_type:
            model_data = data.get("data", {})
            if model_data.get("model", None) == self.websocket_model_name:
                event_data = model_data.get("data", {})
                kwargs = {}
                for key, value in event_data.items():
                    if key in self.model.openapi_types.keys():
                        kwargs[key] = value

                instance = self.model(**kwargs)
        return instance

    @property
    def websocket_model_name(self):
        return self.model.__name__


class WaitForStatusWrapper(WaitForModel):
    model = SimulationStatus
    scenario_name = model.__name__.lower()
    websocket_event_type = "status"


class WaitForProcessedFileWrapper(WaitForModel):
    pass


def match_validated_event(websocket_instance, event: WaitForBase) -> bool:
    if (
        isinstance(websocket_instance, event.model)
        and websocket_instance.id == event.instance.id
    ):
        state = websocket_instance.to_dict().get("state")
        if state == "processing":
            return False
        elif state == "invalid":
            raise ValueError(f"Invalid {event.model}: {websocket_instance.state_detail}")
        elif state == "valid":
            return True

    return False


class WaitForEventValidation(WaitForModel):
    def matches(self, websocket_instance):
        return match_validated_event(websocket_instance, self)


@dataclass
class Time:
    time: int = None
    load: float = None
    simulation_id: str = None

    openapi_types = {"time": "time", "load": "load", "simulation_id": "simulation_id"}


class WaitForTimeWrapper(WaitForBase):
    model = Time
    scenario_name = "waitfortime"
    websocket_event_type = "time"

    def matches(self, websocket_instance):
        if getattr(websocket_instance, "time") >= self._data["time"]:
            return True

        return False


WRAPPERS = [
    WaitForStatusWrapper,
    WaitForTimeWrapper,
]
