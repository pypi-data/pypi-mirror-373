from unittest.mock import AsyncMock

from sqlalchemy import select
from cattle_grid.testing.fixtures import *  # noqa

from cattle_grid.database.activity_pub_actor import StoredActivity
from cattle_grid.model.processing import StoreActivityMessage

from .store_activity import store_activity_subscriber


async def test_store_activity(sql_session_for_test, actor_for_test):
    broker = AsyncMock()
    activity = {
        "actor": actor_for_test.actor_id,
        "type": "Activity",
        "to": ["http://remote.test/actor"],
    }
    msg = StoreActivityMessage(actor=actor_for_test.actor_id, data=activity)

    await store_activity_subscriber(
        msg, actor_for_test, session=sql_session_for_test, broker=broker
    )

    assert 1 == len(
        [x for x in await sql_session_for_test.scalars(select(StoredActivity))]
    )

    broker.publish.assert_awaited_once()
