import pytest

from unittest.mock import AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from faststream.rabbit import RabbitBroker


from cattle_grid.account.account import create_account
from cattle_grid.dependencies.globals import global_container
from cattle_grid.testing.fixtures import *  # noqa

from . import router


@pytest.fixture
def test_app(sql_session_for_test):
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def test_client(test_app):
    return TestClient(test_app)


@pytest.fixture
async def test_token(sql_session_for_test, test_client):
    account = await create_account(sql_session_for_test, "name", "pass")
    assert account
    response = test_client.post(
        "/signin", json={"name": account.name, "password": "pass"}
    )

    assert response.status_code == 200

    return response.json().get("token")


@pytest.fixture
def bearer_header(test_token):
    return {"authorization": f"Bearer {test_token}"}


@pytest.fixture
def test_broker(test_app):
    my_broker = AsyncMock(RabbitBroker)
    test_app.dependency_overrides[global_container.get_broker] = lambda: my_broker

    return my_broker
