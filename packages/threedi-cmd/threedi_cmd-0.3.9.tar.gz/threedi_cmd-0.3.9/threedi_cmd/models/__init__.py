from . import (
    boundary_conditions,
    breach,
    initial_waterlevels,
    lateral,
    leakage,
    postprocessing,
    rain,
    rasteredit,
    revision,
    savedstate,
    settings,
    sources_sinks,
    structure_control,
    substance,
    waitfor,
    wind,
)
from .actions import ActionWrapper
from .simulation import SimulationWrapper

# Define a list of WRAPPERS
# A wrapper is an object that 'wraps' a certain
# resource of the openapi by automatically mapping
# all of it's openapi client methods.

# For every step in a scenario a wrapper is generated

WRAPPERS = (
    [
        ActionWrapper,
        SimulationWrapper,
    ]
    + rain.WRAPPERS
    + savedstate.WRAPPERS
    + waitfor.WRAPPERS
    + lateral.WRAPPERS
    + sources_sinks.WRAPPERS
    + wind.WRAPPERS
    + breach.WRAPPERS
    + rasteredit.WRAPPERS
    + initial_waterlevels.WRAPPERS
    + structure_control.WRAPPERS
    + boundary_conditions.WRAPPERS
    + leakage.WRAPPERS
    + settings.WRAPPERS
    + revision.WRAPPERS
    + postprocessing.WRAPPERS
    + substance.WRAPPERS
)
