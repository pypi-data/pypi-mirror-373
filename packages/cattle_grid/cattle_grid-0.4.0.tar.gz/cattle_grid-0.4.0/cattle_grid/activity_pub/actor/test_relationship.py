import pytest

from cattle_grid.database.activity_pub_actor import Follower
from cattle_grid.testing.fixtures import *  # noqa

from .relationship import followers_for_actor


@pytest.mark.parametrize("accepted,expected", [(True, 1), (False, 0)])
async def test_followers_for_actor(
    sql_session_for_test, actor_for_test, accepted, expected
):
    follower = Follower(
        actor=actor_for_test,
        follower="http://remote.test/follower",
        request="http://remote.test/request_id",
        accepted=accepted,
    )

    sql_session_for_test.add(follower)
    await sql_session_for_test.commit()

    assert (
        len(await followers_for_actor(sql_session_for_test, actor_for_test)) == expected
    )
