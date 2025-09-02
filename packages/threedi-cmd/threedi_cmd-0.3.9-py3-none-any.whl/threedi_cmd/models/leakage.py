from pathlib import Path
from typing import Dict

from threedi_api_client.openapi.models import (
    ConstantLeakage,
    FileRasterLeakage,
    FileTimeseriesLeakage,
    NetCDFRasterLeakage,
    NetCDFTimeseriesLeakage,
    TimeseriesLeakage,
    Upload,
)

from .base import EventWrapper
from .waitfor import WaitForProcessedFileWrapper


class ConstantLeakageWrapper(EventWrapper):
    model = ConstantLeakage
    api_path: str = "leakage_constant"
    scenario_name = model.__name__.lower()


class LeakageTimeseriesWrapper(EventWrapper):
    model = TimeseriesLeakage
    api_path: str = "leakage_timeseries"
    scenario_name = model.__name__.lower()


class WaitForLeakageTimeseriesFileWrapper(WaitForProcessedFileWrapper):
    model = FileTimeseriesLeakage
    scenario_name = model.__name__.lower()


class WaitForLeakageTimeseriesNetCDFWrapper(WaitForLeakageTimeseriesFileWrapper):
    model = NetCDFTimeseriesLeakage
    websocket_model_name = "NetCDFTimeseriesLeakage"
    scenario_name = model.__name__.lower()


class LeakageTimeseriesNetCDFWrapper(EventWrapper):
    model = Upload
    api_path: str = "leakage_timeseries_netcdf"
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
        wait_for_validation = WaitForLeakageTimeseriesNetCDFWrapper(
            data=data, api_client=self._api_client, simulation=self.simulation
        )
        return [wait_for_validation]


class WaitForLeakageRasterFileWrapper(WaitForProcessedFileWrapper):
    model = FileRasterLeakage
    scenario_name = model.__name__.lower()


class WaitForLeakageRasterNetCDFWrapper(WaitForLeakageRasterFileWrapper):
    model = NetCDFRasterLeakage
    websocket_model_name = "NetCDFRasterLeakage"
    scenario_name = model.__name__.lower()


class LeakageRasterNetCDFWrapper(EventWrapper):
    model = Upload
    api_path: str = "leakage_rasters_netcdf"
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
        wait_for_validation = WaitForLeakageRasterNetCDFWrapper(
            data=data, api_client=self._api_client, simulation=self.simulation
        )
        return [wait_for_validation]


WRAPPERS = [
    ConstantLeakageWrapper,
    LeakageTimeseriesWrapper,
    LeakageTimeseriesNetCDFWrapper,
    WaitForLeakageTimeseriesNetCDFWrapper,
    LeakageRasterNetCDFWrapper,
    WaitForLeakageTimeseriesNetCDFWrapper,
]
