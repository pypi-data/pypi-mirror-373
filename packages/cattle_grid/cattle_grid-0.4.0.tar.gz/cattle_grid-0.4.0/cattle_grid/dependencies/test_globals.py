from .globals import global_container, get_engine


async def test_alchemy_database():
    async with global_container.alchemy_database("sqlite+aiosqlite:///:memory:"):
        engine = get_engine()

        assert engine
