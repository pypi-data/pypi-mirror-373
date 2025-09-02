import logging
from pathlib import Path

from threedi_api_client.api import ThreediApi

from threedi_cmd.schematisation_uploader.main import process

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

# TODO: Adjust path to correct path
directory = Path("9_2D_FourCell_Rain/")

with ThreediApi("./staging.env", version="v3-beta") as client:
    schematisation, revision = process(client, directory)
    print(schematisation)
    print(revision)
