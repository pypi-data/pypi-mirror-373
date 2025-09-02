from pathlib import Path
from typing import Dict

from threedi_api_client.openapi.models import (
    ConstantSourcesSinks,
    FileRasterSourcesSinks,
    FileTimeseriesSourcesSinks,
    LizardRasterSourcesSinks,
    LizardTimeseriesSourcesSinks,
    NetCDFRasterSourcesSinks,
    NetCDFTimeseriesSourcesSinks,
    TimeseriesSourcesSinks,
    Upload,
)

from .base import EventWrapper
from .waitfor import WaitForProcessedFileWrapper


class ConstantSourcesSinksWrapper(EventWrapper):
    model = ConstantSourcesSinks
    api_path: str = "sources_sinks_constant"
    scenario_name = model.__name__.lower()


class SourcesSinksTimeseriesWrapper(EventWrapper):
    model = TimeseriesSourcesSinks
    api_path: str = "sources_sinks_timeseries"
    scenario_name = model.__name__.lower()


class SourcesSinksRasterLizardWrapper(EventWrapper):
    model = LizardRasterSourcesSinks
    api_path: str = "sources_sinks_rasters_lizard"
    scenario_name = model.__name__.lower()


class SourcesSinksTimeseriesLizardWrapper(EventWrapper):
    model = LizardTimeseriesSourcesSinks
    api_path: str = "sources_sinks_timeseries_lizard"
    scenario_name = model.__name__.lower()


class WaitForSourcesSinksTimeseriesFileWrapper(WaitForProcessedFileWrapper):
    model = FileTimeseriesSourcesSinks
    scenario_name = model.__name__.lower()


class WaitForSourcesSinksTimeseriesNetCDFWrapper(
    WaitForSourcesSinksTimeseriesFileWrapper
):
    model = NetCDFTimeseriesSourcesSinks
    websocket_model_name = "NetCDFTimeseriesSourcesSinks"
    scenario_name = model.__name__.lower()


class SourcesSinksTimeseriesNetCDFWrapper(EventWrapper):
    model = Upload
    api_path: str = "sources_sinks_timeseries_netcdf"
    scenario_name = model.__name__.lower()
    filepath: Path = None

    def initialize_instance(self, data: Dict):
        self.filepath = Path(data.pop("filepath"))
        super().initialize_instance(data)

    @property
    def extra_steps(self):
        data = {
            "file": {"state": "processed", "filename": self.instance.filename},
            "timeout": 30,
        }
        wait_for_validation = WaitForSourcesSinksTimeseriesNetCDFWrapper(
            data=data, api_client=self._api_client, simulation=self.simulation
        )
        return [wait_for_validation]


class WaitForSourcesSinksRasterFileWrapper(WaitForProcessedFileWrapper):
    model = FileRasterSourcesSinks
    scenario_name = model.__name__.lower()


class WaitForSourcesSinksRasterNetCDFWrapper(WaitForSourcesSinksRasterFileWrapper):
    model = NetCDFRasterSourcesSinks
    websocket_model_name = "NetCDFRasterSourcesSinks"
    scenario_name = model.__name__.lower()


class SourcesSinksRasterNetCDFWrapper(EventWrapper):
    model = Upload
    api_path: str = "sources_sinks_rasters_netcdf"
    scenario_name = model.__name__.lower()
    filepath = None

    def initialize_instance(self, data: Dict):
        self.filepath = Path(data.pop("filepath"))
        super().initialize_instance(data)

    @property
    def extra_steps(self):
        data = {
            "file": {"state": "processed", "filename": self.instance.filename},
            "timeout": 30,
        }
        wait_for_validation = WaitForSourcesSinksRasterNetCDFWrapper(
            data=data, api_client=self._api_client, simulation=self.simulation
        )
        return [wait_for_validation]


WRAPPERS = [
    ConstantSourcesSinksWrapper,
    SourcesSinksTimeseriesWrapper,
    SourcesSinksRasterLizardWrapper,
    SourcesSinksTimeseriesLizardWrapper,
    SourcesSinksTimeseriesNetCDFWrapper,
    WaitForSourcesSinksTimeseriesNetCDFWrapper,
    SourcesSinksRasterNetCDFWrapper,
    WaitForSourcesSinksTimeseriesNetCDFWrapper,
]
