import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.account.account import create_account

from .rabbit import rabbit_router


@pytest.fixture
def test_client():
    app = FastAPI()
    app.include_router(rabbit_router)

    yield TestClient(app)


async def test_user_unauthorized(test_client):
    response = test_client.post(
        "/rabbitmq/user", data={"username": "user", "password": "pass"}
    )

    assert response.status_code == 200
    assert response.text == "deny"


async def test_user(sql_session_for_test, test_client):
    await create_account(sql_session_for_test, "user", "pass")

    response = test_client.post(
        "/rabbitmq/user", data={"username": "user", "password": "pass"}
    )

    assert response.status_code == 200
    assert response.text == "allow"


@pytest.mark.parametrize(
    ["vhost", "result"],
    [("/", "allow"), ("/other", "deny"), ("/some/quite/long", "deny")],
)
async def test_vhost(test_client, vhost, result):
    response = test_client.post(
        "/rabbitmq/vhost", data={"username": "user", "vhost": vhost}
    )

    assert response.text == result


@pytest.mark.parametrize(
    ["name", "routing_key", "result"],
    [
        ("other", "send.user", "deny"),
        ("amq.topic", "other", "deny"),
        ("amq.topic", "send.user.trigger.send_message", "allow"),
        ("amq.topic", "receive.user.incoming", "allow"),
        ("amq.topic", "receive.user.#", "allow"),
        ("amq.topic", "receive.user_other.incoming", "deny"),
        ("amq.topic", "error.user", "allow"),
        ("amq.topic", "error.user_other", "deny"),
    ],
)
async def test_topic(test_client, name, routing_key, result):
    response = test_client.post(
        "/rabbitmq/topic",
        data={"username": "user", "name": name, "routing_key": routing_key},
    )

    assert response.text == result
