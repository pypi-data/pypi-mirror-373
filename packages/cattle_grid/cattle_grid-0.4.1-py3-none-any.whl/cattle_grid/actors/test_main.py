from click.testing import CliRunner

from cattle_grid.testing.cli import *  # noqa

from .__main__ import main


def test_list(db_uri, create_database):
    runner = CliRunner(env={"CATTLE_GRID_DB_URI": db_uri})
    result = runner.invoke(main, ["list"])

    assert result.exit_code == 0
