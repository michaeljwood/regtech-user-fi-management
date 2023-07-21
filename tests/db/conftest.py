import asyncio
import pytest

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from src.entities.models import Base


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    try:
        yield loop
    finally:
        loop.close()


@pytest.fixture(scope="session")
def engine():
    return create_async_engine("sqlite+aiosqlite://")


@pytest.fixture(scope="function", autouse=True)
async def setup_db(
    request: pytest.FixtureRequest,
    engine: AsyncEngine,
    event_loop: asyncio.AbstractEventLoop,
):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    def teardown():
        async def td():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)

        event_loop.run_until_complete(td())

    request.addfinalizer(teardown)


@pytest.fixture(scope="function")
async def session(request: pytest.FixtureRequest, engine: AsyncEngine):
    async with AsyncSession(engine) as session:
        yield session
