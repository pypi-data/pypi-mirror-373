import pytest

from cattle_grid.testing.fixtures import *  # noqa

from cattle_grid.account.account import create_account, add_permission
from cattle_grid.model.account import InformationResponse

from cattle_grid.database.account import ActorForAccount, ActorStatus

from .info import create_information_response


@pytest.fixture
async def test_admin_account(sql_session_for_test):
    account = await create_account(
        sql_session_for_test, "test_account", "test_password"
    )
    assert account
    await add_permission(sql_session_for_test, account, "admin")

    return account


async def test_create_information_response(sql_session_for_test, test_admin_account):
    response = await create_information_response(
        sql_session_for_test, test_admin_account, []
    )

    assert isinstance(response, InformationResponse)


async def test_create_information_response_actors(
    sql_session_for_test,
    test_admin_account,
):
    sql_session_for_test.add_all(
        [
            ActorForAccount(
                account=test_admin_account,
                actor="http://host.test/actor/active",
                status=ActorStatus.active,
            ),
            ActorForAccount(
                account=test_admin_account,
                actor="http://host.test/actor/deleted",
                status=ActorStatus.deleted,
            ),
        ]
    )
    await sql_session_for_test.commit()
    await sql_session_for_test.refresh(test_admin_account, attribute_names=["actors"])

    response = await create_information_response(
        sql_session_for_test, test_admin_account, []
    )

    actors = response.actors
    assert len(actors) == 1

    assert actors[0].id.endswith("active")
