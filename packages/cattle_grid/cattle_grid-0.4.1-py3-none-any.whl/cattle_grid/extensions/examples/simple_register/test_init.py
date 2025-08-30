import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.database.account import Account

from . import extension


@pytest.fixture(autouse=True)
def configure_extension():
    extension.configure(
        {
            "registration_types": [
                {
                    "name": "test_name",
                    "permissions": ["permission_one", "permission_two"],
                    "extra_parameters": ["fediverse"],
                }
            ]
        }
    )


@pytest.fixture
def test_client():
    app = FastAPI()
    app.include_router(extension.api_router)

    return TestClient(app)


def test_register_not_found(test_client):
    response = test_client.post(
        "/register/not_found",
        json={"password": "secret", "name": "alice"},
    )

    assert response.status_code == 404


async def test_register(test_client, sql_session_for_test):
    response = test_client.post(
        "/register/test_name",
        json={
            "password": "secret",
            "name": "alice",
            "fediverse": "acct:alice@host.test",
        },
    )

    assert response.status_code == 201

    account = await sql_session_for_test.scalar(
        select(Account).where(Account.name == "alice")
    )
    assert account

    assert account.meta_information == {
        "fediverse": "acct:alice@host.test",
    }
    await sql_session_for_test.refresh(account, attribute_names=["permissions"])
    assert len(account.permissions) == 2


@pytest.mark.parametrize(
    "body",
    [
        {
            "password": "secret",
            "fediverse": "acct:alice@host.test",
        },
        {
            "password": "secret",
            "name": "alice",
        },
        {"password": "secret", "name": "alice", "fediverse": {"object": True}},
    ],
)
def test_register_invalid(test_client, body):
    response = test_client.post(
        "/register/test_name",
        json=body,
    )

    assert response.status_code == 422


def test_register_duplicate(test_client):
    test_client.post(
        "/register/test_name",
        json={
            "password": "secret",
            "name": "alice",
            "fediverse": "acct:alice@host.test",
        },
    )
    response = test_client.post(
        "/register/test_name",
        json={
            "password": "secret",
            "name": "alice",
            "fediverse": "acct:alice@host.test",
        },
    )

    assert response.status_code == 409
