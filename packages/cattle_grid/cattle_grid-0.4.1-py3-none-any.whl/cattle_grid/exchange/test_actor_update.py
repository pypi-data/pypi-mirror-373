from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.database.account import ActorForAccount
from cattle_grid.model.exchange import UpdateAction, UpdateActionType

from .actor_update import handle_actor_action


async def test_handle_actor_action_rename(
    actor_for_test, account_for_test, sql_session_for_test
):
    actor_for_account = ActorForAccount(
        actor=actor_for_test.actor_id, account=account_for_test
    )
    sql_session_for_test.add(actor_for_account)
    await sql_session_for_test.commit()

    action = UpdateAction(
        action=UpdateActionType.rename,
        name="new name",  # type:ignore
    )

    await handle_actor_action(actor_for_test, sql_session_for_test, action)

    await sql_session_for_test.refresh(actor_for_account)

    assert actor_for_account.name == "new name"
