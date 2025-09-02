from pathlib import Path
from typing import Dict, Optional

from sqlalchemy.orm import Query
from threedi_schema import ThreediDatabase, models

RASTERS_MAP = [
    ("dem_file", models.ModelSettings),
    ("frict_coef_file", models.ModelSettings),
    ("interception_file", models.Interception),
    # Interflow
    ("porosity_file", models.Interflow),
    ("hydraulic_conductivity_file", models.Interflow),
    # Simple infiltration
    ("infiltration_rate_file", models.SimpleInfiltration),
    ("max_infiltration_capacity_file", models.SimpleInfiltration),
    # Groundwater
    ("initial_infiltration_rate_file", models.GroundWater),
    ("equilibrium_infiltration_rate_file", models.GroundWater),
    ("infiltration_decay_period_file", models.GroundWater),
    ("phreatic_storage_capacity_file", models.GroundWater),
    ("groundwater_impervious_layer_level_file", models.GroundWater),
    ("groundwater_hydro_connectivity_file", models.GroundWater),
    # Initials
    ("initial_waterlevel_file", models.InitialConditions),
    ("initial_groundwater_level_file", models.InitialConditions),
    # Vegetation
    ("vegetation_height_file", models.VegetationDrag2D),
    ("vegetation_drag_coefficient_file", models.VegetationDrag2D),
    ("vegetation_stem_count_file", models.VegetationDrag2D),
    ("vegetation_stem_diameter_file", models.VegetationDrag2D),
]


__all__ = ["ModelDB"]


MIN_SQLITE_VERSION = 300


class ModelDB:
    """Interface to sqlite of a model."""

    def __init__(
        self,
        sqlite_path: Path,
        global_settings_id: Optional[int] = None,
        upgrade: bool = False,
    ):
        if not sqlite_path.exists():
            raise ValueError(f"Sqlite path {sqlite_path} does not exist.")

        self.sqlite_path = sqlite_path
        self.database = ThreediDatabase(self.sqlite_path.as_posix())

        version = self.get_version()
        if version < MIN_SQLITE_VERSION:
            if upgrade:
                self.upgrade()
            else:
                raise ValueError(f"Too old sqlite version {version}.")

        if global_settings_id:
            self.global_settings_id = global_settings_id

        try:
            session = self.database.get_session()
            self.model_settings = (
                session.query(models.ModelSettings).order_by("id").first()
            )
            self.global_settings_name = ""
        finally:
            session.close()

    def get_version(self) -> int:
        # check version
        return self.database.schema.get_version()

    def upgrade(self) -> None:
        self.database.schema.upgrade()

    def get_raster_filepaths(self, base_path: Path) -> Dict:
        session = self.database.get_session()
        raster_filepaths = {}
        for raster, db_table in RASTERS_MAP:
            table_contents = Query(db_table).with_session(session).first()
            raster_path = getattr(table_contents, raster, None)
            if raster_path:
                raster_filepaths[raster] = base_path / Path(
                    raster_path.replace("\\", "/")
                )

        session.close()
        return raster_filepaths

    def initial_waterlevels(self):
        try:
            session = self.database.get_session()
            initial_conditions = (
                Query(models.InitialConditions).with_session(session).first()
            )
            initial_waterlevel = (
                initial_conditions.initial_groundwater_level_aggregation,
                initial_conditions.initial_water_level,
            )
            initial_groundwater_level = (
                initial_conditions.initial_groundwater_level_aggregation,
                initial_conditions.initial_groundwater_level,
            )
        finally:
            session.close()
        return initial_waterlevel, initial_groundwater_level
