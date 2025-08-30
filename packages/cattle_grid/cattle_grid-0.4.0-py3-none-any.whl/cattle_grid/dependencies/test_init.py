from unittest.mock import MagicMock
from fast_depends import inject

from . import Config


def test_config():
    mock = MagicMock()

    def tester(config: Config):
        mock(config.db_uri)

    inject(tester)()  # type: ignore

    mock.assert_called_once()
