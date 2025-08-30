import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime
from cattle_grid.testing.fixtures import *  # noqa


from cattle_grid.database.activity_pub_actor import StoredActivity, Follower

from .router_object import ap_router_object


@pytest.fixture
def test_client():
    app = FastAPI()
    app.include_router(ap_router_object)
    yield TestClient(app)


@pytest.fixture
def short_id():
    return "some_id"


@pytest.fixture
def activity_id(short_id):
    return f"http://localhost/object/{short_id}"


@pytest.fixture
async def activity(sql_session_for_test, actor_for_test, short_id, activity_id):  # noqa
    activity_dict = {
        "id": activity_id,
        "actor": actor_for_test.actor_id,
        "type": "Activity",
        "to": ["http://remote.test/actor"],
    }

    sql_session_for_test.add(
        StoredActivity(
            id=short_id,
            actor=actor_for_test,
            data=activity_dict,
            published=datetime.now(),
        )
    )
    await sql_session_for_test.commit()

    return activity_dict


async def test_object_not_found(test_client):
    response = test_client.get(
        "/object/some_id",
        headers={
            "x-cattle-grid-requester": "remote",
            "x-ap-location": "http://localhost/object/some_id",
        },
    )

    assert response.status_code == 404


@pytest.mark.parametrize("requester", ["local", "remote"])
async def test_object_found(
    test_client,
    actor_for_test,
    activity_id,
    activity,
    requester,
):
    response = test_client.get(
        activity_id,
        headers={
            "x-cattle-grid-requester": (
                "http://remote.test/actor"
                if requester == "remote"
                else actor_for_test.actor_id
            ),
            "x-ap-location": activity_id,
        },
    )

    assert response.status_code == 200
    assert response.json() == activity
    assert response.headers["content-type"] == "application/activity+json"


async def test_object_found_follower(
    sql_session_for_test,
    test_client,
    actor_for_test,
    activity_id,
    short_id,
):
    remote_uri = "http://remote.test/actor"

    activity_dict = {
        "id": activity_id,
        "actor": actor_for_test.actor_id,
        "type": "Activity",
        "to": [actor_for_test.followers_uri],
    }
    sql_session_for_test.add_all(
        [
            StoredActivity(
                id=short_id,
                actor=actor_for_test,
                data=activity_dict,
                published=datetime.now(),
            ),
            Follower(
                actor=actor_for_test, follower=remote_uri, accepted=True, request=""
            ),
        ]
    )
    await sql_session_for_test.commit()

    response = test_client.get(
        activity_id,
        headers={
            "x-cattle-grid-requester": remote_uri,
            "x-ap-location": activity_id,
        },
    )

    assert response.status_code == 200
    assert response.json() == activity_dict
    assert response.headers["content-type"] == "application/activity+json"


async def test_object_found_but_unauthorized(
    test_client,
    actor_for_test,
    activity_id,
    activity,
):
    response = test_client.get(
        activity_id,
        headers={
            "x-cattle-grid-requester": "http://other.test",
            "x-ap-location": activity_id,
        },
    )

    assert response.status_code == 401


async def test_object_wrong_domain(
    test_client,
    actor_for_test,
    activity_id,
    activity,
):
    response = test_client.get(
        activity_id,
        headers={
            "x-cattle-grid-requester": actor_for_test.actor_id,
            "x-ap-location": activity_id.replace("localhost", "otherhost"),
        },
    )

    assert response.status_code == 404
