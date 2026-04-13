import pytest

from domain.entities.completion import Completion
from domain.value_objects.completion_status import CompletionStatus
from infrastructure.database.models.completion_model import CompletionModel
from infrastructure.database.repositories.pg_completion_repository import PgCompletionRepository

pytestmark = pytest.mark.integration


async def test_save_persists_success_completion(session):
    completion = Completion(user_id="u1", prompt="hello", model="gemini/gemini-2.5-flash")
    completion.mark_success("response", 100)

    await PgCompletionRepository(session).save(completion)

    row = await session.get(CompletionModel, completion.id)
    assert row is not None
    assert row.user_id == "u1"
    assert row.prompt == "hello"
    assert row.status == CompletionStatus.SUCCESS
    assert row.response == "response"
    assert row.latency_ms == 100
    assert row.error_msg is None


async def test_save_persists_error_completion(session):
    completion = Completion(user_id="u2", prompt="fail", model="gemini/gemini-2.5-flash")
    completion.mark_error("LLM timed out", 0)

    await PgCompletionRepository(session).save(completion)

    row = await session.get(CompletionModel, completion.id)
    assert row is not None
    assert row.status == CompletionStatus.ERROR
    assert row.error_msg == "LLM timed out"
    assert row.response is None
