import pytest
import click

from unittest.mock import MagicMock

from click.testing import CliRunner

from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.testing.cli import *  # noqa

from .account import account_with_name_password, list_permissions
from .cli import add_account_commands, new_account, modify_permissions


@pytest.fixture
def cli(db_uri):
    config = MagicMock()

    config.db_uri = db_uri

    @click.group()
    @click.pass_context
    def main(ctx):
        ctx.ensure_object(dict)
        ctx.obj["config"] = config

    add_account_commands(main)

    return main


def test_new_account_cli(create_database, cli, tmp_path):
    runner = CliRunner()
    result = runner.invoke(cli, ["account", "new", "user", "pass"])

    assert result.exit_code == 0


async def test_new_account(sql_session_for_test):
    await new_account(sql_session_for_test, "user", "pass", permission=["one"])

    account = await account_with_name_password(sql_session_for_test, "user", "pass")

    assert account
    await sql_session_for_test.refresh(account, attribute_names=["permissions"])
    permissions = list_permissions(account)

    assert permissions == ["one"]


async def test_modify_permissions(sql_session_for_test):
    await new_account(sql_session_for_test, "user", "pass", permission=["one"])
    await modify_permissions(sql_session_for_test, "user", ["two"], ["one"])

    account = await account_with_name_password(sql_session_for_test, "user", "pass")

    assert account
    await sql_session_for_test.refresh(account, attribute_names=["permissions"])
    permissions = list_permissions(account)

    assert permissions == ["two"]
