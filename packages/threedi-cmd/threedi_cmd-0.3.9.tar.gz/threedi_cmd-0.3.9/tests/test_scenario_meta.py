import pytest
import yaml

from threedi_cmd.commands.settings import CachedConfig, ScenariosMeta


def test_scenario_meta(tmp_path, scenario_constant_rain_content):
    crf = tmp_path / "constant_rain.yaml"
    with open(crf, "w") as f:
        yaml.dump(
            scenario_constant_rain_content,
            default_flow_style=False,
            stream=f,
        )
    sm = ScenariosMeta(tmp_path)
    assert isinstance(sm.scenarios, list)
    assert len(sm.scenarios) == 1


def test_wrong_scenario_format(tmp_path, cache_content):
    c = CachedConfig(**cache_content)
    f = tmp_path / "test_config.yaml"
    c.save_to_file(f)
    sm = ScenariosMeta(tmp_path)

    with pytest.raises(AttributeError):
        # misses meta section
        sm.scenarios
