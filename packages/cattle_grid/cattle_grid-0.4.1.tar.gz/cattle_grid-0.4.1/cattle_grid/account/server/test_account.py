import asyncio
import pytest
from sqlalchemy import select

from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.database.account import ActorForAccount

from .testing import *  # noqa
from .streaming import get_message_streamer


async def test_stream(test_app, test_client, bearer_header):
    def streamer(account_name, event_type):
        queue = asyncio.Queue()

        async def putter():
            await queue.put("hello")
            await queue.put(account_name)
            await queue.put(None)

        return queue, asyncio.create_task(putter())

    test_app.dependency_overrides[get_message_streamer] = lambda: streamer

    response = test_client.get("/account/stream/incoming", headers=bearer_header)
    assert response.status_code == 200

    assert response.headers["content-type"].split(";")[0] == "text/event-stream"

    assert (
        response.text
        == """data: hello

data: name

"""
    )


@pytest.mark.parametrize("name,expected", [(None, "from_api"), ("alice", "alice")])
async def test_create_actor(
    sql_session_for_test, test_client, bearer_header, name, expected
):
    result = test_client.post(
        "/account/create",
        json={"baseUrl": "http://abel.test", "name": name},
        headers=bearer_header,
    )
    assert result.status_code == 201

    actor_id = result.json()["id"]

    actor = await sql_session_for_test.scalar(
        select(ActorForAccount).where(ActorForAccount.actor == actor_id)
    )
    assert actor
    assert actor.name == expected


def test_create_actor_with_handle(test_client, bearer_header):
    result = test_client.post(
        "/account/create",
        json={"baseUrl": "http://abel.test", "handle": "alice"},
        headers=bearer_header,
    )
    assert result.status_code == 201

    actor = result.json()
    assert actor["preferredUsername"] == "alice"


def test_create_actor_with_handle_duplicate(test_client, bearer_header):
    result = test_client.post(
        "/account/create",
        json={"baseUrl": "http://abel.test", "handle": "alice"},
        headers=bearer_header,
    )
    assert result.status_code == 201

    result = test_client.post(
        "/account/create",
        json={"baseUrl": "http://abel.test", "handle": "alice"},
        headers=bearer_header,
    )
    assert result.status_code == 409
