import pytest

from cattle_grid.testing import mocked_config
from cattle_grid.testing.fixtures import *  # noqa

from .account import create_account, add_permission

from .permissions import allowed_base_urls, can_create_actor_at_base_url

settings_one = {"permissions": {"test_permission": {"base_urls": ["http://one.test"]}}}

settings_admin = {"frontend": {"base_urls": ["http://one.test"]}}


@pytest.fixture
async def test_account(sql_session_for_test):
    account = await create_account(
        sql_session_for_test, "test_account", "test_password"
    )
    assert account
    await add_permission(sql_session_for_test, account, "test_permission")

    return account


@pytest.fixture
async def test_admin_account(sql_session_for_test):
    account = await create_account(
        sql_session_for_test, "test_account", "test_password"
    )
    assert account

    await add_permission(sql_session_for_test, account, "admin")

    return account


async def test_allowed_base_urls_empty(sql_session_for_test, test_account):
    with mocked_config({}):
        result = await allowed_base_urls(sql_session_for_test, test_account)

    assert result == []


async def test_allowed_base_urls(sql_session_for_test, test_account):
    with mocked_config(settings_one):
        result = await allowed_base_urls(
            sql_session_for_test,
            test_account,
        )

    assert result == ["http://one.test"]


async def test_allowed_base_urls_admin(sql_session_for_test, test_admin_account):
    with mocked_config(settings_admin):
        result = await allowed_base_urls(
            sql_session_for_test,
            test_admin_account,
        )

    assert result == ["http://one.test"]


async def test_can_create_actor_at_base_url(sql_session_for_test, test_account):
    with mocked_config({}):
        result = await can_create_actor_at_base_url(
            sql_session_for_test,
            test_account,
            "http://one.test",
        )

    assert not result


async def test_can_create_actor_at_base_url_success(sql_session_for_test, test_account):
    with mocked_config(settings_one):
        result = await can_create_actor_at_base_url(
            sql_session_for_test,
            test_account,
            "http://one.test",
        )

    assert result
