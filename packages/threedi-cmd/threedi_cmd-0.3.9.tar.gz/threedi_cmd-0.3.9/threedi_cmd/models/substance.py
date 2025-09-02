import json
from asyncio import Queue

from threedi_api_client.openapi.models import Simulation, Substance, UploadEventFile

from .base import EventWrapper
from .lateral import FileLateralWrapper


class SubstanceWrapper(EventWrapper):
    model = Substance
    api_path: str = "substance"
    scenario_name = model.__name__.lower()

    async def execute(self, queue: Queue, steps: list) -> list:
        """Create the substance and insert the id into the steps"""
        self.api_substance = self.save()
        return self.insert_substance_id_for_steps(steps)

    def save(self) -> Substance:
        """Create the substance"""
        assert isinstance(self.simulation, Simulation)
        return self._api_client.simulations_substances_create(
            self.simulation.id, self.instance
        )

    def insert_substance_id_for_steps(self, steps: list) -> list:
        """
        Substitute the substance id back into the steps.
        Loop over steps and find substance events with the same id as the instance
        """
        new_steps = []
        for sim_step in steps:
            if hasattr(sim_step.instance, "substances") and isinstance(
                sim_step.instance.substances, list
            ):
                for i, substance in enumerate(sim_step.instance.substances):
                    if substance["substance"] == self.instance.id:
                        sim_step.instance.substances[i]["substance"] = (
                            self.api_substance.id
                        )

            if isinstance(sim_step.instance, UploadEventFile):
                self.insert_substance_id_in_upload_event_file(sim_step)

            new_steps.append(sim_step)

        return new_steps

    def insert_substance_id_in_upload_event_file(self, upload_event: FileLateralWrapper):
        """
        Analyse the upload event file and find the substance id to replace.
        Use the copy of the original bulk event file which is initiated by the wrapper.
        """
        assert upload_event.filepath is not None, "wrapper should be initialized first"

        full_path = self._base_path / upload_event.filepath
        with open(full_path, "r") as file:
            data = json.load(file)

        for i, event in enumerate(data):
            if "substances" in event.keys():
                for j, substance in enumerate(event["substances"]):
                    if substance["substance"] == self.instance.id:
                        data[i]["substances"][j]["substance"] = self.api_substance.id

        # Write updated data back to the file
        with open(full_path, "w") as file:
            json.dump(data, file)


WRAPPERS = [SubstanceWrapper]
