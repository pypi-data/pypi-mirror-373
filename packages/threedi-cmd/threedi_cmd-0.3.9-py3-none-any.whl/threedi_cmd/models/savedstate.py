from threedi_api_client.openapi.models import InitialSavedState, TimedSavedStateUpdate

from .base import InitialWrapper, SimulationChildWrapper


class TimedSavedStateWrapper(SimulationChildWrapper):
    model = TimedSavedStateUpdate
    api_path: str = "create_saved_states_timed"
    scenario_name = model.__name__.lower()


class InitialSavedStateWrapper(InitialWrapper):
    model = InitialSavedState
    api_path: str = "saved_state"
    scenario_name = model.__name__.lower()


WRAPPERS = [TimedSavedStateWrapper, InitialSavedStateWrapper]
