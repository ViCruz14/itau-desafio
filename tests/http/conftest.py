import pytest
import pytest_asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from application.dtos.completion_dto import CreateCompletionOutput
from application.use_cases.create_completion import CreateCompletion
from container import get_create_completion_use_case
from interfaces.http.router import api_router


@pytest.fixture
def mock_output():
    return CreateCompletionOutput(
        id=uuid4(),
        user_id="user-1",
        response="Hi there",
        model="gemini/gemini-2.5-flash",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_use_case(mock_output):
    use_case = AsyncMock(spec=CreateCompletion)
    use_case.execute.return_value = mock_output
    return use_case


@pytest_asyncio.fixture
async def client(mock_use_case):
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[get_create_completion_use_case] = lambda: mock_use_case

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
