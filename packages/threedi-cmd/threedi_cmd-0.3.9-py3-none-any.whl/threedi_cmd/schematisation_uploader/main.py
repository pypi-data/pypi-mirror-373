import logging
import time
from hashlib import md5
from pathlib import Path

from threedi_api_client.files import upload_file
from threedi_api_client.openapi.exceptions import ApiException
from threedi_api_client.openapi.models import (
    Schematisation,
    SchematisationRevision,
    Upload,
)
from threedi_api_client.versions import V3BetaApi

from threedi_cmd.schematisation_uploader.db import ModelDB
from threedi_cmd.schematisation_uploader.yaml_converter import YamlConverter

logger = logging.getLogger(__name__)


def get_md5_sum(path: Path) -> str:
    with path.open("rb") as f:
        file_hash = md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
        return file_hash.hexdigest()


def get_or_create_schematisation(
    client: V3BetaApi,
    name: str,
    organisation_uuid: str = "61f5a464c35044c19bc7d4b42d7f58cb",
) -> Schematisation:
    res = client.schematisations_list(name=name)

    if res.count == 0:
        # Create
        schematisation: Schematisation = client.schematisations_create(
            data={"name": name, "owner": organisation_uuid}
        )
        logger.info(f"Created schematisation {schematisation}")

    else:
        schematisation: Schematisation = res.results[0]
        logger.info(f"Retrieved schematisation {schematisation}")

    return schematisation


def get_or_create_revision(
    client: V3BetaApi,
    schematisation: Schematisation,
    directory: Path,
    valid_timeout: int = 120,
    backoff: int = 5,
) -> SchematisationRevision:
    """
    Only check if the latest revision matches

    valid_timeout => seconds
    backoff: => seconds
    """
    revision: SchematisationRevision | None
    paths = list(directory.glob("*.gpkg"))
    if not paths:
        paths = list(directory.glob("*.sqlite"))
    assert len(paths) == 1
    model_db_path = paths[0]

    try:
        revision = client.schematisations_latest_revision(id=schematisation.id)
        if not revision.is_valid:
            revision = None
    except ApiException:
        revision = None

    model_db = ModelDB(model_db_path, upgrade=True)
    model_db_path = model_db_path.with_suffix(".gpkg")  # sqlite to geopackage
    raster_paths: dict[str, Path] = model_db.get_raster_filepaths(directory / "rasters")

    def is_same(revision: SchematisationRevision) -> bool:
        if sorted([x.type for x in revision.rasters]) != sorted(raster_paths.keys()):
            return False

        # Check sqlite md5sum
        if revision.sqlite.file.etag != get_md5_sum(model_db_path):
            return False

        # Check rasters md5sum
        for raster in revision.rasters:
            if raster.file.etag != get_md5_sum(raster_paths[raster.type]):
                return False

        return True

    if revision and is_same(revision):
        logger.info(f"Revision is already in sync: {revision.id}")
        return revision

    # Need to create the revision
    revision: SchematisationRevision = client.schematisations_revisions_create(
        schematisation_pk=schematisation.id, data={"empty": True}
    )
    logger.info(f"Created new revision: {revision.id}")

    # Upload sqlite
    upload: Upload = client.schematisations_revisions_sqlite_upload(
        id=revision.id,
        schematisation_pk=revision.schematisation_id,
        data={"filename": model_db_path.name.lower()},
    )
    logger.info(f"Uploaded sqlite: {model_db_path.name}")
    upload_file(upload.put_url, model_db_path)
    logger.info("Sqlite uploaded")

    # Upload rasters
    for raster_type, raster_path in raster_paths.items():
        raster = client.schematisations_revisions_rasters_create(
            revision_pk=revision.id,
            schematisation_pk=revision.schematisation_id,
            data={"type": raster_type, "name": raster_path.name.lower()},
        )
        upload: Upload = client.schematisations_revisions_rasters_upload(
            id=raster.id,
            revision_pk=revision.id,
            schematisation_pk=revision.schematisation_id,
            data={"filename": raster_path.name.lower()},
        )
        logger.info(f"Uploading raster: {raster_path.name} [{raster_type}]")
        upload_file(upload.put_url, raster_path)
        logger.info(f"Uploaded raster: {raster_path.name}")

    # Upload initial-waterlevels

    # check if all files have been uploaded
    start_time = time.time()

    def all_uploaded(revision):
        if revision.sqlite.file.state != "uploaded":
            return False
        for raster in revision.rasters:
            if raster.file.state != "uploaded":
                return False
        return True

    logger.info("Waiting for all files to have status 'uploaded'")
    time.sleep(2)
    while (time.time() - start_time) < valid_timeout:
        revision = client.schematisations_revisions_read(
            id=revision.id, schematisation_pk=revision.schematisation_id
        )
        if all_uploaded(revision):
            break
        time.sleep(backoff)

    assert all_uploaded(
        revision
    ), f"Not all files have been successfully uploaded for {revision}"
    logger.info("All files have status 'uploaded'")

    logger.info("Committing...")
    # Commit revision
    client.schematisations_revisions_commit(
        id=revision.id,
        schematisation_pk=revision.schematisation_id,
        data={
            "commit_message": "autocommit new version",
        },
    )

    logger.info("Start waiting for modelchecker result...")
    # Wait until valid (within timeout)
    start_time = time.time()
    while (time.time() - start_time) < valid_timeout:
        time.sleep(backoff)
        revision = client.schematisations_revisions_read(
            id=revision.id, schematisation_pk=revision.schematisation_id
        )
        if revision.is_valid is not None:
            break

    assert revision.is_valid, f"Revision {revision} is not valid!!"
    logger.info("Modelchecker is valid, all done!")
    return revision


def process(
    client: V3BetaApi, directory: Path, organisation_uuid: str, environment: str
) -> tuple[Schematisation, SchematisationRevision]:
    """
    directory: full path to test directory containing sqlite and rasters
        for example: Path("/repo_path_here/9_2D-FourCell_Rain/")
    organisation_uuid: uuid of the organisation that will own the schematisation
    """

    assert directory.is_dir(), "Given path is not a directory"

    schematisation = get_or_create_schematisation(
        client, directory.name, organisation_uuid
    )
    revision = get_or_create_revision(client, schematisation, directory)

    yaml_converter = YamlConverter(environment)
    yaml_converter.convert_yaml(directory / f"{directory.name}.yaml")
    yaml_converter.fill_yaml(
        directory / f"{directory.name}_converted.yaml", schematisation.id, revision.id
    )
    return (schematisation, revision)
