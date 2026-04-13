import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from infrastructure.database.connection import Base
from infrastructure.database.models.completion_model import (  # noqa: F401
    CompletionModel,
)


@pytest.fixture(scope="session")
def postgres_url():
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres.get_connection_url().replace("psycopg2", "asyncpg")


@pytest_asyncio.fixture
async def engine(postgres_url):
    e = create_async_engine(postgres_url, echo=False)
    async with e.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield e
    await e.dispose()


@pytest_asyncio.fixture
async def session(engine):
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
