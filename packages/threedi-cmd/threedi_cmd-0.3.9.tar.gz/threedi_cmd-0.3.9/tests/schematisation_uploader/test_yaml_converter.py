import tempfile
from pathlib import Path

import yaml

from threedi_cmd.schematisation_uploader.yaml_converter import YamlConverter


def test_yaml_converter():
    yaml_converter = YamlConverter()
    content = """
        meta:
            name: "constant rain"
            description: "adds a constant rain event with a duration of 5 minutes at the beginning of the simulation"

        scenario:
            simulation:
                threedimodel: "{{ threedimodel_id }}"
                organisation: "{{ organisation_uuid }}"
                name: "{{ simulation_name }}"
                start_datetime: "{{ datetime_now }}"
                duration: 3600
            steps:
                - constantrain:
                    offset: 0
                    duration: 3600
                    value: 0.00002
                    units: 'm/s'
                - waitforlizardpostprocessing:
                    status: archived
                    timeout: 300
                - substance:
                    name: 'substance1'
                    id: 1
                - waitforstatus:
                    name: 'finished'
                    timeout: 1800
        """
    with tempfile.TemporaryDirectory() as temp_dir:
        yaml_template = Path(temp_dir) / "template.yaml"
        with yaml_template.open("w") as f:
            f.write(content)
        yaml_converter.convert_yaml(yaml_template)

        with open(
            yaml_template.parent / f"{yaml_template.stem}_converted.yaml", "r"
        ) as f:
            converted_content = f.read()
            converted = yaml.load(converted_content, Loader=yaml.FullLoader)

    assert [list(k.keys())[0] for k in converted["scenario"]["steps"]] == [
        "substance",
        "constantrain",
        "action",
        "simulationstatus",
        "waitforlizardpostprocessing",
    ]
