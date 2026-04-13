from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from container import get_settings
from infrastructure.database.connection import build_engine, build_session_factory
from infrastructure.llm.litellm_provider import LiteLLMProvider
from interfaces.http.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    engine = build_engine(settings)
    app.state.engine = engine
    app.state.session_factory = build_session_factory(engine)
    app.state.llm_provider = LiteLLMProvider(settings)
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Itau LLM Gateway",
        version="1.0.0",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url=None,
        lifespan=lifespan,
    )
    app.include_router(api_router)
    return app


app = create_app()
