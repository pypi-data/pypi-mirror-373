from fastapi import FastAPI
from contextlib import asynccontextmanager

from cattle_grid.dependencies.globals import global_container
from cattle_grid.database.auth import Base
from cattle_grid.version import __version__
from .router import auth_router

__all__ = ["auth_router"]


def create_app():
    """Allows running just the auth endpoint"""

    @asynccontextmanager
    async def lifespan(app):
        async with global_container.alchemy_database() as engine:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            yield

    app = FastAPI(
        lifespan=lifespan,
        title="cattle_grid.auth",
        description="""Authorization server for Fediverse applications. It basically checks HTTP Signatures for you.""",
        version=__version__,
    )

    app.include_router(auth_router)

    return app
