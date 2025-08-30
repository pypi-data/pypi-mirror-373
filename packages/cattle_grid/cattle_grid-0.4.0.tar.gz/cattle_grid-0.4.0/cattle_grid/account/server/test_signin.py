import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.account.account import create_account

from cattle_grid.dependencies.globals import global_container

from . import router


@pytest.fixture
def test_client():
    app = FastAPI()
    app.include_router(router)

    return TestClient(app)


@pytest.fixture
async def test_account(sql_session_for_test):
    account = await create_account(sql_session_for_test, "name", "pass")

    return account


def test_signin_missing_data(test_client, test_account):
    response = test_client.post("/signin", json={"name": "name"})

    assert response.status_code == 422


def test_signin_wrong_password(test_client, test_account):
    response = test_client.post("/signin", json={"name": "name", "password": "wrong"})

    assert response.status_code == 401


def test_signin(test_client, test_account):
    response = test_client.post("/signin", json={"name": "name", "password": "pass"})

    global_container.method_information = []

    assert response.status_code == 200

    data = response.json()

    assert "token" in data

    response = test_client.get(
        "/account/info", headers={"Authorization": f"Bearer {data['token']}"}
    )

    assert response.status_code == 200


@pytest.mark.parametrize("endpoint", ["/account/info"])
def test_unauthorized_without_signin(endpoint, test_client):
    response = test_client.get(endpoint)
    assert response.status_code == 401
