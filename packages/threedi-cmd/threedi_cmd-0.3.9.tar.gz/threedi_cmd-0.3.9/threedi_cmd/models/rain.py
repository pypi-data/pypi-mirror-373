from pathlib import Path
from typing import Callable, Dict

from threedi_api_client.openapi.models import (
    ConstantLocalRain,
    ConstantRain,
    FileRasterRain,
    FileTimeseriesRain,
    LizardRasterRain,
    LizardTimeseriesRain,
    NetCDFRasterRain,
    NetCDFTimeseriesRain,
    TimeseriesLocalRain,
    TimeseriesRain,
    Upload,
)

from .base import EventWrapper
from .waitfor import WaitForProcessedFileWrapper


def reference_uuid_environment_converter(config: dict, **kwargs: dict) -> dict:
    """Return environment corrected configuration"""
    assert (
        "reference_uuid" in config
    ), f"Reference UUID not found in configuration: {config}"

    if isinstance(config["reference_uuid"], str):
        # Reference UUID is already a string, no need to resolve
        return config

    assert isinstance(config["reference_uuid"], dict), (
        f"Attempting to resolve reference UUID from environment "
        f"but config is not a dict: {config}"
    )

    environment = kwargs.get("environment", "production")
    config["reference_uuid"] = config["reference_uuid"][environment]
    return config


class ConstantRainWrapper(EventWrapper):
    model = ConstantRain
    api_path: str = "rain_constant"
    scenario_name = model.__name__.lower()


class LocalConstantRainWrapper(EventWrapper):
    model = ConstantLocalRain
    api_path: str = "rain_local_constant"
    scenario_name = model.__name__.lower()


class RainTimeseriesWrapper(EventWrapper):
    model = TimeseriesRain
    api_path: str = "rain_timeseries"
    scenario_name = model.__name__.lower()


class LocalRainTimeseriesWrapper(EventWrapper):
    model = TimeseriesLocalRain
    api_path: str = "rain_local_timeseries"
    scenario_name = model.__name__.lower()


class RainRasterLizardWrapper(EventWrapper):
    model = LizardRasterRain
    api_path: str = "rain_rasters_lizard"
    scenario_name = model.__name__.lower()
    converters: list[Callable] = [reference_uuid_environment_converter]


class RainTimeseriesLizardWrapper(EventWrapper):
    model = LizardTimeseriesRain
    api_path: str = "rain_timeseries_lizard"
    scenario_name = model.__name__.lower()
    converters: list[Callable] = [reference_uuid_environment_converter]


class WaitForProcessedTimeseriesFileWrapper(WaitForProcessedFileWrapper):
    model = FileTimeseriesRain
    scenario_name = model.__name__.lower()


class WaitForRainTimeseriesNetCDFWrapper(WaitForProcessedTimeseriesFileWrapper):
    model = NetCDFTimeseriesRain
    websocket_model_name = "NetCDFTimeseriesRain"
    scenario_name = model.__name__.lower()


class RainTimeseriesNetCDFWrapper(EventWrapper):
    model = Upload
    api_path: str = "rain_timeseries_netcdf"
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
        wait_for_validation = WaitForRainTimeseriesNetCDFWrapper(
            data=data, api_client=self._api_client, simulation=self.simulation
        )
        return [wait_for_validation]


class WaitForProcessedRasterFileWrapper(WaitForProcessedFileWrapper):
    model = FileRasterRain
    scenario_name = model.__name__.lower()


class WaitForRainRasterNetCDFWrapper(WaitForProcessedRasterFileWrapper):
    model = NetCDFRasterRain
    websocket_model_name = "NetCDFRasterRain"
    scenario_name = model.__name__.lower()


class RainRasterNetCDFWrapper(EventWrapper):
    model = Upload
    api_path: str = "rain_rasters_netcdf"
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
        wait_for_validation = WaitForRainRasterNetCDFWrapper(
            data=data, api_client=self._api_client, simulation=self.simulation
        )
        return [wait_for_validation]


WRAPPERS = [
    ConstantRainWrapper,
    RainTimeseriesWrapper,
    RainRasterLizardWrapper,
    RainTimeseriesLizardWrapper,
    RainTimeseriesNetCDFWrapper,
    WaitForRainTimeseriesNetCDFWrapper,
    RainRasterNetCDFWrapper,
    WaitForRainTimeseriesNetCDFWrapper,
    LocalConstantRainWrapper,
    LocalRainTimeseriesWrapper,
]
