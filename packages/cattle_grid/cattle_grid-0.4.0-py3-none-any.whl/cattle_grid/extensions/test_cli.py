import os
import json
from click.testing import CliRunner

from .__main__ import main


def test_open_api(tmp_path):
    filename = tmp_path / "openapi.json"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "openapi",
            "cattle_grid.extensions.examples.simple_storage",
            "--filename",
            str(filename),
        ],
    )

    assert result.exit_code == 0
    assert os.path.exists(filename)

    with open(filename, "r") as fp:
        schema = json.load(fp)

    assert isinstance(schema, dict)
