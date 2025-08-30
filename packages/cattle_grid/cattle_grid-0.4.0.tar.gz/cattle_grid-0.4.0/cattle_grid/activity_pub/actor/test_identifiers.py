import pytest

from cattle_grid.testing.fixtures import *  # noqa

from cattle_grid.database.activity_pub_actor import (
    PublicIdentifier,
    PublicIdentifierStatus,
)

from .identifiers import collect_identifiers_for_actor, identifier_in_list_exists


def test_collect_identifiers_for_actor(actor_for_test):
    identifiers = collect_identifiers_for_actor(actor_for_test)

    assert identifiers == [actor_for_test.actor_id]


async def test_collect_identifiers_for_actor_with_acct_uri(
    sql_session_for_test, actor_for_test
):
    sql_session_for_test.add(
        PublicIdentifier(
            actor=actor_for_test,
            name="webfinger",
            identifier="acct:me@localhost",
            status=PublicIdentifierStatus.verified,
            preference=5,
        )
    )
    await sql_session_for_test.commit()
    await sql_session_for_test.refresh(actor_for_test, attribute_names=["identifiers"])

    identifiers = collect_identifiers_for_actor(actor_for_test)

    assert identifiers == ["acct:me@localhost", actor_for_test.actor_id]


async def test_collect_identifiers_for_actor_with_acct_uri_unverified(
    sql_session_for_test, actor_for_test
):
    sql_session_for_test.add(
        PublicIdentifier(
            actor=actor_for_test,
            name="webfinger",
            identifier="acct:me@localhost",
            status=PublicIdentifierStatus.unverified,
            preference=5,
        )
    )
    await sql_session_for_test.commit()
    await sql_session_for_test.refresh(actor_for_test, attribute_names=["identifiers"])

    identifiers = collect_identifiers_for_actor(actor_for_test)

    assert identifiers == [actor_for_test.actor_id]


@pytest.mark.parametrize(
    "identifiers, expected",
    [
        ([], False),
        (["acct:one@localhost"], True),
        (["acct:other@localhost"], False),
        (["acct:other@localhost", "acct:one@localhost"], True),
    ],
)
async def test_identifier_in_list_exists(
    session_maker_for_tests, actor_for_test, identifiers, expected
):
    async with session_maker_for_tests() as session:
        session.add(
            PublicIdentifier(
                actor_id=actor_for_test.id,
                name="webfinger",
                identifier="acct:one@localhost",
                status=PublicIdentifierStatus.unverified,
                preference=5,
            )
        )
        session.add(
            PublicIdentifier(
                actor_id=actor_for_test.id,
                name="webfinger",
                identifier="acct:two@localhost",
                status=PublicIdentifierStatus.unverified,
                preference=5,
            )
        )
        await session.commit()
    async with session_maker_for_tests() as session:
        result = await identifier_in_list_exists(session, identifiers)

    assert result == expected
