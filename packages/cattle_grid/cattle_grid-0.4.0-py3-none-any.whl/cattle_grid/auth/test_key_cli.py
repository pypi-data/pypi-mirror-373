import pytest
import click

from click.testing import CliRunner

from dynaconf import LazySettings
from .key_cli import add_keys_command


@pytest.fixture
def cli(tmp_path):
    @click.group()
    @click.pass_context
    def main(ctx):
        ctx.ensure_object(dict)
        ctx.obj["config"] = LazySettings()

        ctx.obj["config_file"] = str(tmp_path / "config.toml")

    add_keys_command(main)

    return main


def test_handle_no_config():
    @click.group()
    @click.pass_context
    def main(ctx):
        ctx.ensure_object(dict)

    add_keys_command(main)
    runner = CliRunner()

    result = runner.invoke(main, ["keys", "clear"])
    assert result.exit_code == 1


def test_keys_command(cli):
    runner = CliRunner()
    result = runner.invoke(cli, ["keys", "clear"])
    assert result.exit_code == 0
