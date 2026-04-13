import os

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from config.settings import Settings


@pytest_asyncio.fixture
async def engine():
    settings = Settings()
    url = os.getenv("TEST_DATABASE_URL", settings.database_url)
    e = create_async_engine(url, echo=False)
    yield e
    await e.dispose()


@pytest_asyncio.fixture
async def session(engine):
    """
    Wraps each test in a transaction rolled back at teardown.
    The 'create_savepoint' mode makes session.commit() release a SAVEPOINT
    instead of committing the outer transaction, preserving test isolation.
    """
    async with engine.connect() as conn:
        await conn.begin()
        s = AsyncSession(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        yield s
        await s.close()
        await conn.rollback()
