import pytest

from sqlalchemy.ext.asyncio import async_sessionmaker

from cattle_grid.account.account import create_account, add_actor_to_account
from cattle_grid.activity_pub.actor import create_actor

from cattle_grid.config.auth import new_auth_config, save_auth_config
from cattle_grid.dependencies.globals import global_container

from cattle_grid.database.activity_pub import Base as APBase


@pytest.fixture(autouse=True)
async def sql_engine_for_tests():
    """Provides the sql engine (as in memory sqlite) for tests"""
    async with global_container.alchemy_database(
        "sqlite+aiosqlite:///:memory:", echo=False
    ) as engine:  # type: ignore
        async with engine.begin() as conn:
            await conn.run_sync(APBase.metadata.create_all)

        yield engine


@pytest.fixture()
async def session_maker_for_tests(sql_engine_for_tests):
    yield async_sessionmaker(sql_engine_for_tests, expire_on_commit=False)


@pytest.fixture()
async def sql_session_for_test(session_maker_for_tests):
    async with session_maker_for_tests() as session:
        yield session


@pytest.fixture
async def account_for_test(sql_session_for_test):
    """Fixture to create an account"""
    return await create_account(
        sql_session_for_test, "alice", "alice", permissions=["admin"]
    )


@pytest.fixture
async def actor_for_test(sql_session_for_test):
    """Fixture to create an actor"""
    actor = await create_actor(sql_session_for_test, "http://localhost/ap")

    return actor


@pytest.fixture
async def actor_with_account(sql_session_for_test, account_for_test):
    """Fixture to create an actor with an account"""
    actor = await create_actor(sql_session_for_test, "http://localhost/ap")
    await add_actor_to_account(
        sql_session_for_test, account_for_test, actor, name="test_fixture"
    )

    await sql_session_for_test.refresh(actor)

    return actor


@pytest.fixture
def auth_config():
    config = new_auth_config(actor_id="http://localhost/actor_id", username="actor")

    config.domain_blocks = set(["blocked.example"])

    return config


@pytest.fixture
def auth_config_file(tmp_path, auth_config):
    filename = tmp_path / "auth_config.toml"

    save_auth_config(filename, auth_config)

    return filename


@pytest.fixture(autouse=True, scope="session")
def loaded_config():
    """Ensures the configuration variables are loaded"""
    global_container.load_config()
