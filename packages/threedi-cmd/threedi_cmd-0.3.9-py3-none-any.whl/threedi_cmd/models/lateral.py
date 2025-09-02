import shutil
from pathlib import Path
from typing import Callable

from threedi_api_client.openapi.models import (
    ConstantLateral,
    FileLateral,
    TimeseriesLateral,
    UploadEventFile,
)

from .base import EventWrapper
from .waitfor import WaitForEventValidation


def filename_converter(config: dict, **kwargs: dict) -> dict:
    """Return environment corrected configuration"""
    config["filename"] = config.pop("file")
    return config


class WaitForConstantLateralWrapper(WaitForEventValidation):
    model = ConstantLateral
    scenario_name = model.__name__.lower()


class WaitForTimeseriesLateralWrapper(WaitForEventValidation):
    model = TimeseriesLateral
    scenario_name = model.__name__.lower()


class WaitForFileLateralWrapper(WaitForEventValidation):
    model = FileLateral
    scenario_name = model.__name__.lower()


class ConstantLateralWrapper(EventWrapper):
    model = ConstantLateral
    api_path: str = "lateral_constant"
    scenario_name = model.__name__.lower()

    @property
    def extra_steps(self):
        wait_for_validation = WaitForConstantLateralWrapper(
            data=self.instance.to_dict(),
            api_client=self._api_client,
            simulation=self.simulation,
        )
        return [wait_for_validation]


class TimeseriesLateralWrapper(EventWrapper):
    model = TimeseriesLateral
    api_path: str = "lateral_timeseries"
    scenario_name = model.__name__.lower()

    @property
    def extra_steps(self):
        wait_for_validation = WaitForTimeseriesLateralWrapper(
            data=self.instance.to_dict(),
            api_client=self._api_client,
            simulation=self.simulation,
        )
        return [wait_for_validation]


class FileLateralWrapper(EventWrapper):
    model = UploadEventFile
    api_path: str = "lateral_file"
    scenario_name = "filelateral"
    filepath: Path | None = None
    converters: list[Callable] = [filename_converter]

    def initialize_instance(self, data: dict | None = None) -> None:
        # Create a copy of the file
        assert data is not None
        converted_file = f"{data['filename'].split('.')[0]}_converted.json"
        full_path = self._base_path / converted_file
        if full_path.exists():
            full_path.unlink()
        shutil.copy(self._base_path / data["filename"], full_path)

        # Set the filepath
        data["filename"] = converted_file
        self.filepath = Path(converted_file)
        super().initialize_instance(data)

    @property
    def extra_steps(self):
        file_laterals = self.api.simulations_events_lateral_file_list(
            simulation_pk=self.simulation.id
        )
        for file_lateral in file_laterals.results:
            if file_lateral.file and file_lateral.file.filename == self.instance.filename:
                bulk_event_instance = file_lateral
                break
        assert bulk_event_instance is not None

        wait_for_validation = WaitForFileLateralWrapper(
            data=bulk_event_instance.to_dict(),
            api_client=self._api_client,
            simulation=self.simulation,
        )
        return [wait_for_validation]


WRAPPERS = [
    # WaitForConstantLateralWrapper,
    # WaitForTimeseriesLateralWrapper,
    # WaitForFileLateralWrapper,
    ConstantLateralWrapper,
    TimeseriesLateralWrapper,
    FileLateralWrapper,
]
