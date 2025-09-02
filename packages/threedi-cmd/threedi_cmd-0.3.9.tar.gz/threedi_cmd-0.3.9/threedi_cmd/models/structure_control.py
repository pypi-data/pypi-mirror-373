from pathlib import Path
from typing import Dict

from threedi_api_client.openapi.models import (
    FileStructureControl,
    MemoryStructureControl,
    TableStructureControl,
    TimedStructureControl,
)
from threedi_api_client.openapi.models.upload_event_file import UploadEventFile

from .base import EventWrapper
from .waitfor import (
    WaitForEventValidation,
    match_validated_event,
)


class WaitForTimedStructureControlWrapper(WaitForEventValidation):
    model = TimedStructureControl
    scenario_name = model.__name__.lower()

    def matches(self, websocket_instance):
        return match_validated_event(websocket_instance, self)


class TimedStructureControlWrapper(EventWrapper):
    model = TimedStructureControl
    api_path: str = "structure_control_timed"
    scenario_name = model.__name__.lower()

    @property
    def extra_steps(self):
        wait_for_validation = WaitForTimedStructureControlWrapper(
            data=self.instance.to_dict(),
            api_client=self._api_client,
            simulation=self.simulation,
        )
        return [wait_for_validation]


class WaitForTableStructureControlWrapper(WaitForEventValidation):
    model = TableStructureControl
    scenario_name = model.__name__.lower()

    def matches(self, websocket_instance):
        return match_validated_event(websocket_instance, self)


class TableStructureControlWrapper(EventWrapper):
    model = TableStructureControl
    api_path: str = "structure_control_table"
    scenario_name = model.__name__.lower()

    @property
    def extra_steps(self):
        wait_for_validation = WaitForTableStructureControlWrapper(
            data=self.instance.to_dict(),
            api_client=self._api_client,
            simulation=self.simulation,
        )
        return [wait_for_validation]


class WaitForMemoryStructureControlWrapper(WaitForEventValidation):
    model = MemoryStructureControl
    scenario_name = model.__name__.lower()

    def matches(self, websocket_instance):
        return match_validated_event(websocket_instance, self)


class MemoryStructureControlWrapper(EventWrapper):
    model = MemoryStructureControl
    api_path: str = "structure_control_memory"
    scenario_name = model.__name__.lower()

    @property
    def extra_steps(self):
        wait_for_validation = WaitForMemoryStructureControlWrapper(
            data=self.instance.to_dict(),
            api_client=self._api_client,
            simulation=self.simulation,
        )
        return [wait_for_validation]


class WaitForFileStructureControlWrapper(WaitForEventValidation):
    model = FileStructureControl
    scenario_name = model.__name__.lower()

    def matches(self, websocket_instance):
        return match_validated_event(websocket_instance, self)


class FileStructureControlWrapper(EventWrapper):
    model = UploadEventFile
    api_path: str = "structure_control_file"
    scenario_name = model.__name__.lower()
    filepath: Path = None

    def initialize_instance(self, data: Dict):
        self.filepath = Path(data.pop("filepath"))
        super().initialize_instance(data)

    @property
    def extra_steps(self):
        file_controls = self.api.simulations_events_structure_control_file_list(
            simulation_pk=self.simulation.id
        )
        for file_control in file_controls.results:
            if file_control.file and file_control.file.filename == self.instance.filename:
                bulk_control_instance = file_control
                break
        assert bulk_control_instance is not None

        wait_for_validation = WaitForFileStructureControlWrapper(
            data=bulk_control_instance.to_dict(),
            api_client=self._api_client,
            simulation=self.simulation,
        )
        return [wait_for_validation]


WRAPPERS = [
    TimedStructureControlWrapper,
    WaitForTimedStructureControlWrapper,
    TableStructureControlWrapper,
    WaitForTableStructureControlWrapper,
    MemoryStructureControlWrapper,
    WaitForMemoryStructureControlWrapper,
    FileStructureControlWrapper,
    WaitForFileStructureControlWrapper,
]
