import asyncio
import json
from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from typing import Dict, List, NoReturn, Optional

from dateutil import parser
from rich.padding import Padding
from rich.progress import (
    BarColumn,
    Progress,
    Task,
    TextColumn,
    TimeRemainingColumn,
)

from threedi_cmd.commands.settings import (
    get_settings,
)
from threedi_cmd.console import console
from threedi_cmd.websockets.clients import WebsocketClient

MAX_LEN_NAME = 30


class StatusColors:
    starting = "gold3"
    initialized = ""
    finished = "green"
    postprocessing = "royal_blue1"
    crashed = "red"
    ended = "dodger_blue1"


class MessageTypes(Enum):
    initial = "active-simulations"
    progress = "progress"
    status = "status"
    new = "active-simulation"


progress = Progress(
    TextColumn(
        "[bold blue]ID {task.fields[sim_id]} | {task.fields[status]}",
        justify="left",
    ),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    TextColumn("[bold cyan]{task.fields[name]}", justify="left"),
    "•",
    TextColumn("[bold]{task.fields[user]}", justify="left"),
    "•",
    TextColumn("[bold dark_goldenrod]{task.fields[organisation]}", justify="left"),
    "•",
    TimeRemainingColumn(),
    console=console,
    auto_refresh=False,
    # transient=True
)


@dataclass
class ProgressInfo:
    # defaults are used for the header,
    # instance overrides these values
    sim_id: str = "ID"
    progress: str = "PROGRESS"
    name: str = "NAME"
    user: str = "USER"
    organisation: str = "ORGANISATION"
    time_reamining: str = "TIME REMAINING"

    @classmethod
    def header(cls):
        return f"Currently running simulations [{cls.sim_id} • {cls.progress} • {cls.name} • {cls.user} • {cls.organisation} • {cls.time_reamining}]"  # noqa


@dataclass
class ProgressTask(ProgressInfo):
    """
    every progress bar is managed through a rich.progress.Task.
    This class holds all task related info, plus the actual
    rich.progress.Task instance called 'task'
    """

    description: str = "running"
    start: bool = field(init=False)
    total: int = 100
    status: str = ""
    task: Task = None
    is_live: bool = False

    _kwarg_fields = {
        "description",
        "sim_id",
        "name",
        "user",
        "organisation",
        "start",
        "total",
        "status",
    }

    def __post_init__(self):
        self.start = True if self.progress else False

    @property
    def kwargs(self) -> Dict:
        d = {field_name: getattr(self, field_name) for field_name in self._kwarg_fields}
        return {k: v for k, v in d.items() if not k.startswith("_")}


class ActiveSimulations:
    STATUS_COLORS = {
        "starting": "gold3",
        "initialized": "",
        "finished": "green",
        "postprocessing": "royal_blue1",
        "crashed": "red",
        "ended": "dodger_blue1",
    }

    def __init__(self, endpoint: str):
        self.endpoint = endpoint  # local | stag | prod
        # local cache {simulation_id: ProgressTask}
        self.tasks = {}

    @cached_property
    def websocket_client(self):
        settings = get_settings(self.endpoint)
        return WebsocketClient(settings=settings.websocket_settings)

    async def add_progress_bar(
        self, progress_task: ProgressTask, progress: Progress
    ) -> None:
        """creates a new progress task and adds a ProgressTask instance to the internal registry"""
        task_id = progress.add_task(**progress_task.kwargs)
        if progress_task.progress:
            progress.update(task_id, advance=int(progress_task.progress))
        task = [t for t in progress.tasks if t.id == task_id][0]
        progress_task.task = task
        self.tasks[int(progress_task.sim_id)] = progress_task

    async def advance_progress(self, data: Dict, progress: Progress) -> None:
        """advances the progress bar for the given tasks by the current simulation progress"""
        simulation_id = data["data"]["simulation_id"]
        sim_progress = data["data"]["progress"]
        progress_task = self.tasks.get(int(simulation_id))
        if not progress_task.task.started:
            progress.start_task(progress_task.task.id)
        if int(sim_progress) <= progress_task.task.percentage:
            return
        advance_by = int(sim_progress) - int(progress_task.task.percentage)
        progress.update(progress_task.task.id, advance=advance_by)
        # auto_refresh is False so do this manually
        progress.refresh()

    @staticmethod
    def is_live_finished(status, progress_task: ProgressTask) -> bool:
        return all(
            (
                status == "crashed",
                progress_task.is_live,
                progress_task.status in ("ended", "postprocessing"),
            )
        )

    async def update_status(self, data: Dict, progress: Progress):
        status = data["data"]["status"]
        simulation_id = data["data"]["simulation_id"]
        progress_task = self.tasks.get(int(simulation_id))
        if self.is_live_finished(status, progress_task):
            status = "finished"
        status_txt = status
        color = self.STATUS_COLORS.get(status)
        if color:
            status_txt = f"[bold {color}]{status_txt}[/bold {color}]"
        update_kwargs = {"status": status_txt}
        advance_by = 100 if status in ("finished", "ended", "postprocessing") else None
        if advance_by and not progress_task.task.started:
            progress.start_task(progress_task.task.id)
            update_kwargs.update({"advance": advance_by})
        progress.update(progress_task.task.id, **update_kwargs)
        # auto_refresh is False so do this manually
        progress.refresh()
        progress_task.status = status

    async def run_monitor(self) -> NoReturn:
        asyncio.ensure_future(self.websocket_client.listen("active-simulations/"))
        q = self.websocket_client.get_queue()
        try:
            await asyncio.wait_for(self.websocket_client.is_connected(), timeout=10)
        except asyncio.TimeoutError:
            console.print("Could not establish WS connection", style="error")
            return
        with progress:
            progress.console.print(Padding("", (1, 0)))
            progress.console.rule(ProgressInfo.header())
            progress.console.print(Padding("", (1, 0)))
            while True:
                data = await q.get()
                message_type = await self.get_msg_type(data)
                if not message_type:
                    continue
                if message_type == MessageTypes.initial:
                    progress_tasks = await self.get_initial_progress_tasks(data)
                    for progress_task in progress_tasks:
                        await self.add_progress_bar(progress_task, progress)
                elif message_type == MessageTypes.progress:
                    await self.advance_progress(data, progress)
                elif message_type == MessageTypes.status:
                    await self.update_status(data, progress)
                elif message_type == MessageTypes.new:
                    progress_task = await self.get_new_progress_task(data)
                    await self.add_progress_bar(progress_task, progress)

    @staticmethod
    async def get_msg_type(data) -> Optional[MessageTypes]:
        try:
            return MessageTypes(data["type"])
        except (KeyError, ValueError):
            return

    @staticmethod
    async def get_new_progress_task(data):
        """
        message from "active-simulations" URI
        type declaration "active-simulation"
        """
        data = data["data"]
        simulation_id = list(data.keys())[0]
        data_json = list(data.values())[0]
        return await ActiveSimulations._get_progress_task(simulation_id, data_json)

    @staticmethod
    async def _get_progress_task(simulation_id, simulation_details) -> ProgressTask:
        details = json.loads(simulation_details)
        if len(details["name"]) > MAX_LEN_NAME:
            name = f"{details['name'][:MAX_LEN_NAME]}..."
        else:
            name = details["name"]

        is_live = int(details["duration"]) == 3153600000
        if is_live:
            dt = parser.parse(details["date_created"])
            name = f"{name} | {dt.strftime('%Y-%m-%d %H:%M')} [bold red][LIVE][/bold red]"
        sim_progress = details["progress"]
        return ProgressTask(
            sim_id=simulation_id,
            name=name,
            user=details["user_name"],
            organisation=details["organisation_name"],
            progress=sim_progress,
            status=details["status"],
            is_live=is_live,
        )

    @staticmethod
    async def get_initial_progress_tasks(data: Dict) -> List[ProgressTask]:
        progress_tasks = []
        for simulation_id, json_details in data["data"].items():
            task_info = await ActiveSimulations._get_progress_task(
                simulation_id, json_details
            )
            progress_tasks.append(task_info)
        return progress_tasks
