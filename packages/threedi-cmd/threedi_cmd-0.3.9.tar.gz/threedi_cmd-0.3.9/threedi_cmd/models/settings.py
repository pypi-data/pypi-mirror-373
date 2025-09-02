from threedi_api_client.openapi.models import (
    AggregationSettings,
    NumericalSettings,
    PhysicalSettings,
    TimeStepSettings,
)

from .base import SettingsWrapper


class PhysicalSettingsWrapper(SettingsWrapper):
    model = PhysicalSettings
    api_path: str = "physical"
    scenario_name = model.__name__.lower()


class NumercialSettingsWrapper(SettingsWrapper):
    model = NumericalSettings
    api_path: str = "numerical"
    scenario_name = model.__name__.lower()


class TimeStepSettingsWrapper(SettingsWrapper):
    model = TimeStepSettings
    api_path: str = "time_step"
    scenario_name = model.__name__.lower()


class AggregationSettingsWrapper(SettingsWrapper):
    model = AggregationSettings
    api_path: str = "aggregation"
    scenario_name = model.__name__.lower()


WRAPPERS = [
    PhysicalSettingsWrapper,
    NumercialSettingsWrapper,
    TimeStepSettingsWrapper,
    AggregationSettingsWrapper,
]
