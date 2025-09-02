import asyncio
import time
from asyncio import Queue
from typing import Dict

from threedi_api_client.openapi.models import (
    ArrivalTimePostProcessing,
    BasicPostProcessing,
    DamagePostProcessing,
    PostProcessingStatus,
)

from threedi_cmd.console import console

from .base import LizardPostprocessingWrapper
from .waitfor import DEFAULT_TIMEOUT, WaitForTimeout


class LizardBasicPostprocessingWrapper(LizardPostprocessingWrapper):
    model = BasicPostProcessing
    api_path: str = "basic"
    scenario_name = "lizardbasicpostprocessing"


class LizardDamagePostprocessingWrapper(LizardPostprocessingWrapper):
    model = DamagePostProcessing
    api_path: str = "damage"
    scenario_name = "lizarddamagepostprocessing"


class LizardArrivalPostprocessingWrapper(LizardPostprocessingWrapper):
    model = ArrivalTimePostProcessing
    api_path: str = "arrival"
    scenario_name = "lizardarrivalpostprocessing"


class WaitForLizardPostprocessingWrapper(LizardPostprocessingWrapper):
    """
    Wait for a Lizard Postprocessing status to be what is specified
    """

    model = PostProcessingStatus
    scenario_name = "waitforlizardpostprocessing"
    extra_fields = ["timeout"]

    def __init__(self, data: Dict, *args, **kwargs):
        if "timeout" in data:
            self.timeout = data.pop("timeout")
        else:
            self.timeout = DEFAULT_TIMEOUT
        super().__init__(data, *args, **kwargs)

    async def execute(self, queue: Queue, steps: list) -> list:
        status = None
        console.rule(
            f'[bold] Waiting for Lizard PostProcessingStatus(status="{self.instance.status}") (timeout: {self.timeout} seconds)',
            style="gold3",
        )
        end_statuses = ["archived", "archiving_failed"]

        start = time.time()
        while True:
            resp = self.api.simulations_results_post_processing_lizard_status_list(
                self.simulation.id
            )
            status = resp.status.lower()
            if status in end_statuses:
                break
            if time.time() - start > self.timeout:
                raise WaitForTimeout(
                    f"Lizard postprocessing result {self.instance.status} not found within timeout"
                )
            await asyncio.sleep(2)

        if status != self.instance.status:
            raise ValueError(f"Expected status {self.instance.status}, got {status}")

        return steps


WRAPPERS = [
    LizardBasicPostprocessingWrapper,
    LizardDamagePostprocessingWrapper,
    LizardArrivalPostprocessingWrapper,
    WaitForLizardPostprocessingWrapper,
]
