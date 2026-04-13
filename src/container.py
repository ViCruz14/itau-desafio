from collections.abc import AsyncGenerator
from functools import lru_cache

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.ports.llm_provider import LLMProvider
from application.use_cases.create_completion import CreateCompletion
from config.settings import Settings
from infrastructure.database.repositories.pg_completion_repository import (
    PgCompletionRepository,
)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def _get_session_factory(request: Request) -> async_sessionmaker[AsyncSession]:
    return request.app.state.session_factory


def get_llm_provider(request: Request) -> LLMProvider:
    return request.app.state.llm_provider


async def get_db_session(
    session_factory: async_sessionmaker[AsyncSession] = Depends(_get_session_factory),
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


async def get_create_completion_use_case(
    session: AsyncSession = Depends(get_db_session),
    llm_provider: LLMProvider = Depends(get_llm_provider),
    settings: Settings = Depends(get_settings),
) -> CreateCompletion:
    return CreateCompletion(
        llm_provider=llm_provider,
        completion_repository=PgCompletionRepository(session),
        model=settings.llm_model,
    )
