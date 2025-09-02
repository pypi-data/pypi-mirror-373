from threedi_api_client.openapi.models import Simulation

from .base import ModelWrapper


class SimulationWrapper(ModelWrapper):
    model = Simulation
    api_path = "simulations"
    scenario_name = model.__name__.lower()
