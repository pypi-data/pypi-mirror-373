from threedi_api_client.openapi.models import (
    ConstantWind,
    TimeseriesWind,
    WindDragCoefficient,
)

from .base import EventWrapper, InitialWrapper


class WindDragCoefficientWrapper(InitialWrapper):
    model = WindDragCoefficient
    api_path = "wind_drag_coefficient"
    scenario_name = model.__name__.lower()


class ConstantWindWrapper(EventWrapper):
    model = ConstantWind
    api_path: str = "wind_constant"
    scenario_name = model.__name__.lower()


class TimeseriesWindWrapper(EventWrapper):
    model = TimeseriesWind
    api_path: str = "wind_timeseries"
    scenario_name = model.__name__.lower()


WRAPPERS = [
    WindDragCoefficientWrapper,
    ConstantWindWrapper,
    TimeseriesWindWrapper,
]
