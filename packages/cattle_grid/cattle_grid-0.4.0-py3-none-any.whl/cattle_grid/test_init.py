from .testing.fixtures import *  # noqa

from . import create_app


def test_create_app(auth_config_file, sql_engine_for_tests):  # noqa
    create_app([auth_config_file])
