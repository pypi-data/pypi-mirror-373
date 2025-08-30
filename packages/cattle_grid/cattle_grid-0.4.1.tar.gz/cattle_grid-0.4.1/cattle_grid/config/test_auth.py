import pytest

from dynaconf import Dynaconf

from cattle_grid.testing.fixtures import auth_config_file, auth_config  # noqa

from .auth import get_auth_config, AuthNotConfigured, AuthConfig, new_auth_config
from .settings import get_settings


def test_get_auth_config_blank():
    with pytest.raises(AuthNotConfigured):
        get_auth_config(settings=Dynaconf())


def test_get_auth_blank(auth_config_file):  # noqa
    result = get_auth_config(get_settings([auth_config_file]))

    assert isinstance(result, AuthConfig)


def test_new_auth_config():
    config = new_auth_config("http://localhost/cattle_grid_actor")

    assert config.actor_acct_id.startswith("acct:")
    assert config.actor_acct_id.endswith("@localhost")
