import logging
import secrets

from urllib.parse import urljoin, urlparse

from bovine import BovineActor
from bovine.activitystreams import Actor as AsActor, factories_for_actor_object
from bovine.activitystreams.utils.property_value import property_value_context
from bovine.crypto import generate_rsa_public_private_key
from bovine.types import Visibility
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


from cattle_grid.database.activity_pub_actor import (
    Actor,
    PublicIdentifier,
    Follower,
    Following,
    ActorStatus,
    PublicIdentifierStatus,
)
from cattle_grid.database.activity_pub import Credential

from .identifiers import (
    determine_preferred_username,
    collect_identifiers_for_actor,
    identifier_in_list_exists,
)
from .helper import endpoints_object_from_actor_id

logger = logging.getLogger(__name__)


class DuplicateIdentifierException(Exception):
    """Raised if an identifier already exists and one tries to create an actor with it"""


def new_url(base_url: str, url_type: str) -> str:
    token = secrets.token_urlsafe(16)
    return urljoin(base_url, f"{url_type}/{token}")


def compute_acct_uri(base_url: str, preferred_username: str):
    """Computes the acct uri

    ```pycon
    >>> compute_acct_uri("http://host.example/somewhere", "alice")
    'acct:alice@host.example'

    ```

    """
    host = urlparse(base_url).hostname

    return f"acct:{preferred_username}@{host}"


async def create_actor(
    session: AsyncSession,
    base_url: str,
    preferred_username: str | None = None,
    identifiers: dict = {},
    profile: dict = {},
):
    """Creates a new actor in the database"""

    public_key, private_key = generate_rsa_public_private_key()
    public_key_name = "legacy-key-1"
    actor_id = new_url(base_url, "actor")

    if preferred_username:
        if "webfinger" in identifiers:
            raise ValueError("webfinger key set in identifiers")
        identifiers = {
            **identifiers,
            "webfinger": compute_acct_uri(base_url, preferred_username),
        }

    if "activitypub_id" not in identifiers:
        identifiers = {**identifiers, "activitypub_id": actor_id}

    identifier_already_exists = await identifier_in_list_exists(
        session, list(identifiers.values())
    )

    if identifier_already_exists:
        raise DuplicateIdentifierException("identifier already exists")

    actor = Actor(
        actor_id=actor_id,
        inbox_uri=new_url(base_url, "inbox"),
        outbox_uri=new_url(base_url, "outbox"),
        following_uri=new_url(base_url, "following"),
        followers_uri=new_url(base_url, "followers"),
        public_key_name=public_key_name,
        public_key=public_key,
        profile=profile,
        automatically_accept_followers=False,
        status=ActorStatus.active,
    )
    session.add(actor)

    for name, identifier in identifiers.items():
        session.add(
            PublicIdentifier(
                actor=actor,
                name=name,
                identifier=identifier,
                status=PublicIdentifierStatus.verified,
            )
        )

    credential = Credential(
        actor_id=actor_id,
        identifier=f"{actor_id}#{public_key_name}",
        secret=private_key,
    )
    session.add(credential)

    logging.info("Created actor with id '%s'", actor_id)

    await session.commit()
    await session.refresh(actor, attribute_names=["identifiers"])

    return actor


def actor_to_object(actor: Actor) -> dict:
    """Transform the actor to an object

    :params actor:
    :returns:
    """

    sorted_identifiers = collect_identifiers_for_actor(actor)

    preferred_username = determine_preferred_username(
        sorted_identifiers, actor.actor_id
    )
    attachments = actor.profile.get("attachment")
    result = AsActor(
        id=actor.actor_id,
        outbox=actor.outbox_uri,
        inbox=actor.inbox_uri,
        followers=actor.followers_uri,
        following=actor.following_uri,
        public_key=actor.public_key,
        public_key_name=actor.public_key_name,
        preferred_username=preferred_username,
        type=actor.profile.get("type", "Person"),
        name=actor.profile.get("name"),
        summary=actor.profile.get("summary"),
        url=actor.profile.get("url"),
        icon=actor.profile.get("image", actor.profile.get("icon")),
        properties={
            "attachment": attachments,
            "published": actor.created_at.isoformat(),
        },
    ).build(visibility=Visibility.OWNER)

    result["identifiers"] = sorted_identifiers
    result["endpoints"] = endpoints_object_from_actor_id(actor.actor_id)

    if attachments:
        result["@context"].append(property_value_context)

    return result


async def bovine_actor_for_actor_id(
    session: AsyncSession, actor_id: str
) -> BovineActor | None:
    """Uses the information stored in
    [Credential][cattle_grid.database.activity_pub.Credential] to construct a bovine actor

    :params actor_id:
    :returns:
    """
    credential = await session.scalar(
        select(Credential).where(Credential.actor_id == actor_id)
    )

    if credential is None:
        logger.warning("No credential found for %s", actor_id)
        return None

    return BovineActor(
        public_key_url=credential.identifier,
        actor_id=actor_id,
        secret=credential.secret,
    )


def update_for_actor_profile(actor: Actor) -> dict:
    """Creates an update for the Actor"""

    actor_profile = actor_to_object(actor)
    activity_factory, _ = factories_for_actor_object(actor_profile)

    return (
        activity_factory.update(actor_profile, followers=actor_profile["followers"])
        .as_public()
        .build()
    )


def delete_for_actor_profile(actor: Actor) -> dict:
    """Creates a delete activity for the Actor"""

    actor_profile = actor_to_object(actor)
    activity_factory, _ = factories_for_actor_object(actor_profile)

    result = (
        activity_factory.delete(
            actor_profile.get("id"), followers=actor_profile["followers"]
        )
        .as_public()
        .build()
    )

    result["cc"].append(actor_profile["following"])

    return result


async def delete_actor(session: AsyncSession, actor: Actor):
    """Deletes an actor

    :param actor: Actor to be deleted
    """
    await session.execute(
        delete(PublicIdentifier).where(PublicIdentifier.actor_id == actor.id)
    )
    actor.status = ActorStatus.deleted
    await session.commit()


async def remove_from_followers_following(
    session: AsyncSession, actor_id_to_remove: str
):
    """Removes actor_id from all occurring followers and following"""
    await session.execute(
        delete(Follower).where(Follower.follower == actor_id_to_remove)
    )
    await session.execute(
        delete(Following).where(Following.following == actor_id_to_remove)
    )
