import pytest
import click

from unittest.mock import MagicMock

from click.testing import CliRunner

from .block_cli import add_block_command


@pytest.fixture
def config():
    settings = MagicMock()
    return settings


@pytest.fixture
def cli(tmp_path, config):
    @click.group()
    @click.pass_context
    def main(ctx):
        ctx.ensure_object(dict)
        ctx.obj["config"] = config
        ctx.obj["config_file"] = str(tmp_path / "config.toml")
        ctx.obj["config_file"] = str(tmp_path / "config.toml")
        ctx.obj["config_file_block_list"] = str(tmp_path / "config_block_list.toml")

    add_block_command(main)

    return main


def test_handle_no_config():
    @click.group()
    @click.pass_context
    def main(ctx):
        ctx.ensure_object(dict)

    add_block_command(main)
    runner = CliRunner()

    result = runner.invoke(main, ["block", "empty"])
    assert result.exit_code == 1


def test_keys_command(cli):
    runner = CliRunner()
    result = runner.invoke(cli, ["block", "empty"])

    assert result.exit_code == 0


def test_block_list_command(config, cli):
    config.domain_blocks = {"bad.example", "worse.example"}
    runner = CliRunner()
    result = runner.invoke(cli, ["block", "list"])

    assert result.exit_code == 0

    assert (
        result.stdout
        == """bad.example
worse.example
"""
    )
