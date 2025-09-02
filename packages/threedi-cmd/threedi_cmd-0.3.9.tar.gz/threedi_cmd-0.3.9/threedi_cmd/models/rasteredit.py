from typing import Dict

from threedi_api_client.openapi.api.v3_api import V3Api
from threedi_api_client.openapi.models import RasterEdit

from .base import EventWrapper


class RasterEditError(Exception):
    pass


class RasterEditWrapper(EventWrapper):
    model = RasterEdit
    api_path: str = "raster_edits"
    scenario_name = model.__name__.lower()
    raster_type = None

    def initialize_instance(self, data: Dict):
        self.raster_type = data.pop("raster__type", None)
        if self.raster_type is None and "raster" not in data:
            raise RasterEditError(
                f"Please proved either `raster__type` or `raster`the RasterEdit: {data}"
            )

        if self.raster_type is not None:
            # Try to lookup/find the raster.
            api: V3Api = self._api_client
            res = api.threedimodels_rasters_list(
                self.simulation.threedimodel_id, type=self.raster_type
            )
            if res.count != 1:
                raise RasterEditError(
                    f"Could not find raster_type, raster_list response whas {res}"
                )

            # Set raster
            data["raster"] = res.results[0].id

        super().initialize_instance(data)


WRAPPERS = [RasterEditWrapper]
