from sqlalchemy import func
from .database import database_session
from .database.auth import RemoteIdentity
from cattle_grid.database.activity_pub_actor import Actor


async def statistics(config):
    async with database_session(db_uri=config.db_uri) as session:
        remote_identity_count = await session.scalar(func.count(RemoteIdentity.id))
        actor_count = await session.scalar(func.count(Actor.id))

        print(f"Remote identity count: {remote_identity_count:10d}")
        print(f"Actor count:           {actor_count:10d}")
