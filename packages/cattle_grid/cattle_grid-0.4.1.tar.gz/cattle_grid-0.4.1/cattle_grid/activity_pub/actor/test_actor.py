import pytest
from datetime import datetime, timezone
from bovine import BovineActor
from sqlalchemy import select
from sqlalchemy.sql import func

from cattle_grid.database.activity_pub import Credential
from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.database.activity_pub_actor import (
    Actor,
    PublicIdentifier,
    Follower,
    Following,
    ActorStatus,
)


from . import (
    create_actor,
    actor_to_object,
    compute_acct_uri,
    bovine_actor_for_actor_id,
    update_for_actor_profile,
    delete_for_actor_profile,
    delete_actor,
    remove_from_followers_following,
    DuplicateIdentifierException,
)


async def test_create_actor(sql_session_for_test):
    actor = await create_actor(sql_session_for_test, "http://localhost/ap/")

    await sql_session_for_test.refresh(actor)

    assert actor.actor_id.startswith("http://localhost/ap/actor/")

    assert 1 == await sql_session_for_test.scalar(func.count(Actor.id))


async def test_create_then_delete_actor(sql_session_for_test):
    actor = await create_actor(
        sql_session_for_test, "http://localhost/ap/", preferred_username="me"
    )
    await delete_actor(sql_session_for_test, actor)

    assert 1 == await sql_session_for_test.scalar(func.count(Actor.id))
    await sql_session_for_test.refresh(actor)

    assert actor.status == ActorStatus.deleted

    assert 0 == await sql_session_for_test.scalar(func.count(PublicIdentifier.id))
    assert 1 == await sql_session_for_test.scalar(select(func.count(Credential.id)))


async def test_actor_to_object(sql_session_for_test):
    actor = await create_actor(sql_session_for_test, "http://localhost/ap/")

    actor.created_at = datetime(2020, 4, 7, 12, 56, 12, tzinfo=timezone.utc)

    obj = actor_to_object(actor)

    assert obj["type"] == "Person"

    assert obj.get("followers")
    assert obj["published"] == "2020-04-07T12:56:12+00:00"


async def test_update_for_actor_profile(sql_session_for_test):
    actor = await create_actor(sql_session_for_test, "http://localhost/ap/")

    activity = update_for_actor_profile(actor)

    assert activity["type"] == "Update"
    obj = activity["object"]

    assert obj["type"] == "Person"
    assert activity["cc"]


async def test_actor_to_object_with_profile(sql_session_for_test):
    actor = await create_actor(
        sql_session_for_test,
        "http://localhost/ap/",
        profile={"name": "Alice Newton", "type": "Application"},
    )

    obj = actor_to_object(actor)

    assert obj["type"] == "Application"

    assert obj.get("name") == "Alice Newton"


async def test_actor_to_object_with_image(sql_session_for_test):
    actor = await create_actor(
        sql_session_for_test,
        "http://localhost/ap/",
        profile={"image": {"type": "Image"}},
    )

    obj = actor_to_object(actor)

    assert obj["icon"] == {"type": "Image"}


async def test_create_actor_with_identifiers(sql_session_for_test):
    identifier = "acct:you@localhost"
    await create_actor(
        sql_session_for_test,
        "http://localhost/ap/",
        identifiers={"webfinger": identifier},
    )

    pi = await sql_session_for_test.scalar(
        select(PublicIdentifier).where(PublicIdentifier.identifier == identifier)
    )

    assert pi

    assert pi.name == "webfinger"
    assert pi.identifier == identifier


async def test_create_actor_with_preferred_username(sql_session_for_test):
    identifier = "acct:me@localhost"
    actor = await create_actor(
        sql_session_for_test, "http://localhost/ap/", preferred_username="me"
    )

    pi = await sql_session_for_test.scalar(
        select(PublicIdentifier).where(PublicIdentifier.identifier == identifier)
    )

    assert pi

    assert pi.name == "webfinger"
    assert pi.identifier == identifier

    profile = actor_to_object(actor)
    assert profile["preferredUsername"] == "me"


def test_compute_webfinger():
    webfinger = compute_acct_uri("http://localhost/ap", "me")

    assert webfinger == "acct:me@localhost"


async def test_get_bovine_actor_not_found(sql_session_for_test):
    bovine_actor = await bovine_actor_for_actor_id(
        sql_session_for_test, "http://nothing.here/actor"
    )

    assert bovine_actor is None


async def test_get_bovine_actor(sql_session_for_test):
    actor = await create_actor(sql_session_for_test, "http://localhost/ap/")

    bovine_actor = await bovine_actor_for_actor_id(sql_session_for_test, actor.actor_id)

    assert isinstance(bovine_actor, BovineActor)


async def test_delete_for_actor_profile(sql_session_for_test):
    actor = await create_actor(sql_session_for_test, "http://localhost/ap/")

    activity = delete_for_actor_profile(actor)

    assert activity["type"] == "Delete"

    assert activity["object"] == actor.actor_id


async def test_remove_from_followers_following(sql_session_for_test):
    actor = await create_actor(sql_session_for_test, "http://localhost/ap/")

    remote_id = "http://remote.test"

    follower = Follower(actor=actor, follower=remote_id, accepted=True, request="")
    following = Following(actor=actor, following=remote_id, accepted=True, request="")

    sql_session_for_test.add_all([follower, following])
    await sql_session_for_test.commit()

    await remove_from_followers_following(sql_session_for_test, remote_id)

    assert 0 == await sql_session_for_test.scalar(func.count(Follower.id))
    assert 0 == await sql_session_for_test.scalar(func.count(Following.id))


async def test_identifier_ordering(sql_session_for_test):
    actor = await create_actor(sql_session_for_test, "http://localhost/ap/")

    one = PublicIdentifier(
        actor=actor, name="one", identifier="acct:jekyll@localhost", preference=1
    )
    two = PublicIdentifier(
        actor=actor, name="two", identifier="acct:hyde@localhost", preference=100
    )
    sql_session_for_test.add_all([one, two])
    await sql_session_for_test.commit()

    await sql_session_for_test.refresh(actor, attribute_names=["identifiers"])

    result = actor_to_object(actor)

    assert result["identifiers"] == [
        "acct:hyde@localhost",
        "acct:jekyll@localhost",
        actor.actor_id,
    ]
    assert result["preferredUsername"] == "hyde"

    one.preference = 1000
    await sql_session_for_test.merge(one)
    await sql_session_for_test.commit()
    await sql_session_for_test.refresh(actor, attribute_names=["identifiers"])

    result = actor_to_object(actor)

    assert result["identifiers"] == [
        "acct:jekyll@localhost",
        "acct:hyde@localhost",
        actor.actor_id,
    ]
    assert result["preferredUsername"] == "jekyll"


async def test_create_actor_duplicate_preferred_username(sql_session_for_test):
    await create_actor(
        sql_session_for_test, "http://localhost/ap/", preferred_username="me"
    )

    with pytest.raises(DuplicateIdentifierException):
        await create_actor(
            sql_session_for_test, "http://localhost/ap/", preferred_username="me"
        )


async def test_actor_to_object_attachments(sql_session_for_test):
    property_value_context = {
        "PropertyValue": {
            "@id": "https://schema.org/PropertyValue",
            "@context": {
                "value": "https://schema.org/value",
                "name": "https://schema.org/name",
            },
        }
    }
    property_value = {
        "type": "PropertyValue",
        "name": "key",
        "value": "value",
    }
    actor = await create_actor(
        sql_session_for_test,
        "http://localhost/ap/",
        profile={"attachment": [property_value]},
    )

    result = actor_to_object(actor)

    assert result["attachment"] == [property_value]
    assert property_value_context in result["@context"]
