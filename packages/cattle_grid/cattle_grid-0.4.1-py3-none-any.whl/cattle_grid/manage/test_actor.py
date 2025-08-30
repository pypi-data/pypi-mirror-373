from cattle_grid.testing.fixtures import *  # noqa

from . import ActorManager


async def test_actor_manager_profile(actor_for_test, sql_session_for_test):
    manager = ActorManager(
        actor_id=actor_for_test.actor_id, session=sql_session_for_test
    )

    result = await manager.profile(sql_session_for_test)

    assert result["id"] == actor_for_test.actor_id
    assert len(result["identifiers"]) > 0
