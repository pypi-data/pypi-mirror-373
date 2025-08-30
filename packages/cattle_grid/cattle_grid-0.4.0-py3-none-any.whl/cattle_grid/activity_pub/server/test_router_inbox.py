import pytest
import json
from unittest.mock import AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from bovine.crypto.helper import content_digest_sha256_rfc_9530

from .router_inbox import ap_router_inbox

from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.dependencies.globals import global_container


@pytest.fixture
def test_app():
    app = FastAPI()
    app.include_router(ap_router_inbox)
    return app


@pytest.fixture
def test_client(test_app):
    yield TestClient(test_app)


@pytest.fixture
def mock_broker(test_app):
    mock = AsyncMock()

    test_app.dependency_overrides[global_container.get_broker] = lambda: mock

    return mock


@pytest.mark.parametrize("uri_func", [lambda x: x.inbox_uri, lambda x: "/shared_inbox"])
@pytest.mark.parametrize(
    ("data", "headers"),
    [
        ({}, {}),
        ({}, {"x-cattle-grid-requester": "owner"}),
        ({"actor": "other"}, {"x-cattle-grid-requester": "owner"}),
    ],
)
async def test_inbox_unauthorized(
    uri_func,
    data,
    headers,
    test_client,
    actor_for_test,  # noqa
):
    body = json.dumps(data)
    key, val = content_digest_sha256_rfc_9530(body.encode())
    response = test_client.post(
        uri_func(actor_for_test),
        content=body,
        headers={
            key: val,
            "x-cattle-grid-requester": "owner",
            "x-ap-location": actor_for_test.inbox_uri,
        },
    )

    assert response.status_code == 401


@pytest.mark.parametrize("uri_func", [lambda x: x.inbox_uri, lambda x: "/shared_inbox"])
async def test_inbox(test_client, actor_for_test, mock_broker, uri_func):  # noqa
    body = b'{"actor": "owner", "type": "AnimalSound"}'
    key, val = content_digest_sha256_rfc_9530(body)

    response = test_client.post(
        uri_func(actor_for_test),
        content=body,
        headers={
            key: val,
            "x-cattle-grid-requester": "owner",
            "x-ap-location": actor_for_test.inbox_uri,
        },
    )

    assert response.status_code == 202

    mock_broker.publish.assert_awaited_once()


@pytest.mark.parametrize("uri_func", [lambda x: x.inbox_uri, lambda x: "/shared_inbox"])
async def test_inbox_no_digest(test_client, actor_for_test, mock_broker, uri_func):  # noqa
    response = test_client.post(
        uri_func(actor_for_test),
        json={"actor": "owner"},
        headers={
            "x-cattle-grid-requester": "owner",
            "x-ap-location": actor_for_test.inbox_uri,
        },
    )

    assert response.status_code == 400


@pytest.mark.parametrize("uri_func", [lambda x: x.inbox_uri, lambda x: "/shared_inbox"])
async def test_inbox_unprocessable(test_client, actor_for_test, uri_func):  # noqa
    body = b'{"xxxx"}'
    key, val = content_digest_sha256_rfc_9530(body)

    response = test_client.post(
        uri_func(actor_for_test),
        headers={
            key: val,
            "content-type": "text/plain",
            "x-cattle-grid-requester": "owner",
            "x-ap-location": actor_for_test.inbox_uri,
        },
        content=body,
    )

    assert response.status_code == 422


async def test_endpoint_not_found_inbox(test_client):
    response = test_client.post(
        "http://localhost/ap/inbox/not_an_actor",
        headers={
            "x-cattle-grid-requester": "owner",
            "x-ap-location": "http://localhost/ap/inbox/not_an_actor",
        },
    )

    assert response.status_code == 404
