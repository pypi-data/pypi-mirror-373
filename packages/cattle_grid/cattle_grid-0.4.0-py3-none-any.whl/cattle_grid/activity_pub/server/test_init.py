import pytest

from urllib.parse import urlparse
from fastapi import FastAPI
from fastapi.testclient import TestClient
from cattle_grid.activity_pub.actor import create_actor

from cattle_grid.testing.fixtures import *  # noqa

from . import router


@pytest.fixture
def test_client():
    app = FastAPI()
    app.include_router(router)

    yield TestClient(app)


async def test_webfinger_plain(test_client):
    response = test_client.get("/ap/.well-known/webfinger")

    assert response.status_code == 422


async def test_webfinger_not_found(test_client):
    response = test_client.get(
        "/ap/.well-known/webfinger", params={"resource": "acct:unknown@nowhere"}
    )

    assert response.status_code == 404


async def test_webfinger_found(test_client, sql_session_for_test):
    identifier = "acct:me@localhost"

    await create_actor(
        sql_session_for_test,
        "http://localhost/ap/",
        identifiers={"webfinger": identifier},
    )

    response = test_client.get(
        "/ap/.well-known/webfinger", params={"resource": identifier}
    )

    assert response.status_code == 200


async def test_nodeinfo(test_client):
    response = test_client.get(
        "/ap/.well-known/nodeinfo",
        headers={"x-ap-location": "http://testserver/.well-known/nodeinfo"},
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data["links"]) == 1

    link = data["links"][0]

    assert link["type"] == "http://nodeinfo.diaspora.software/ns/schema/2.0"
    assert link["href"] == "http://testserver/.well-known/nodeinfo_2.0"

    node_info_response = test_client.get("/ap" + urlparse(link["href"]).path)
    assert node_info_response.status_code == 200

    assert node_info_response.headers["content-type"] == "application/jrd+json"
