from pathlib import Path

from threedi_cmd.commands.settings import CachedConfig


def test_load_cached_config_no_file():
    c = CachedConfig.load_from_file(Path(""))
    assert isinstance(c, CachedConfig)


def test_save_and_load(tmp_path, cache_content):
    c = CachedConfig(**cache_content)
    f = tmp_path / "test_config.yaml"
    c.save_to_file(f)
    assert f.exists() and f.is_file()
    rc = CachedConfig.load_from_file(f)
    assert rc == c
