from dataclasses import dataclass
from typing import Callable, Literal
import logging


from bovine import BovineActor
from bovine.crypto.types import CryptographicIdentifier
from fediverse_pasture.server.utils import actor_object_to_public_key
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from cattle_grid.database.auth import RemoteIdentity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def result_for_identity(identity: RemoteIdentity):
    if identity.controller == "gone":
        return None

    return CryptographicIdentifier.from_tuple(identity.controller, identity.public_key)


@dataclass
class PublicKeyCache:
    """Caches public keys in the database and fetches them
    using bovine_actor"""

    bovine_actor: BovineActor
    """used to fetch the public key"""

    session_maker: Callable[[], AsyncSession] | None = None
    """sql session maker"""

    async def cryptographic_identifier(
        self, key_id: str
    ) -> CryptographicIdentifier | Literal["gone"] | None:
        """Returns "gone" if Tombstone

        :param key_id: URI of the public key to fetch
        :returns:
        """

        try:
            result = await self.bovine_actor.get(key_id)

            if result is None:
                return "gone"

            if result.get("type") == "Tombstone":
                logger.info("Got Tombstone for %s", key_id)
                return "gone"

            public_key, owner = actor_object_to_public_key(result, key_id)

            if public_key is None or owner is None:
                return None

            return CryptographicIdentifier.from_pem(public_key, owner)
        except Exception as e:
            logger.info("Failed to fetch public key for %s with %s", key_id, repr(e))
            logger.exception(e)
            return None

    async def from_cache(self, key_id: str) -> CryptographicIdentifier | None:
        if not self.session_maker:
            raise Exception("Sql session must be set")

        async with self.session_maker() as session:
            try:
                identity = await session.scalar(
                    select(RemoteIdentity).where(RemoteIdentity.key_id == key_id)
                )
            except Exception as e:
                logger.exception(e)
                identity = None

            if identity:
                return result_for_identity(identity)

            identifier = await self.cryptographic_identifier(key_id)
            if identifier is None:
                return None

            if identifier == "gone":
                session.add(
                    RemoteIdentity(key_id=key_id, public_key="gone", controller="gone")
                )
                await session.commit()
                return None

            try:
                controller, public_key = identifier.as_tuple()

                session.add(
                    RemoteIdentity(
                        key_id=key_id, public_key=public_key, controller=controller
                    )
                )
                await session.commit()
            except Exception as e:
                logger.exception(e)
            return identifier
