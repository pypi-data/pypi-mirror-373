import tomli_w
from . import load_settings


def test_load_config_new_file(tmp_path):
    config = load_settings(tmp_path / "doesnotexist.toml")

    assert not config.enable_reporting


def test_load_config_existing_file(tmp_path):
    filename = tmp_path / "config.toml"
    with open(filename, "wb") as fp:
        tomli_w.dump({"enable_reporting": True}, fp)
    config = load_settings(filename)

    assert config.enable_reporting
