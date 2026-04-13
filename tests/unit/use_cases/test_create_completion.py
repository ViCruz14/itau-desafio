import pytest
from unittest.mock import AsyncMock

from application.dtos.completion_dto import CreateCompletionInput
from application.use_cases.create_completion import CreateCompletion
from domain.value_objects.completion_status import CompletionStatus

MODEL = "gemini/gemini-2.5-flash"


@pytest.fixture
def llm_provider():
    return AsyncMock()


@pytest.fixture
def repository():
    return AsyncMock()


@pytest.fixture
def use_case(llm_provider, repository):
    return CreateCompletion(
        llm_provider=llm_provider,
        completion_repository=repository,
        model=MODEL,
    )


async def test_execute_returns_output_dto(use_case, llm_provider):
    llm_provider.complete.return_value = ("response text", 150)

    output = await use_case.execute(CreateCompletionInput(user_id="u1", prompt="hello"))

    assert output.response == "response text"
    assert output.user_id == "u1"
    assert output.model == MODEL


async def test_execute_saves_completion_with_success_status(use_case, llm_provider, repository):
    llm_provider.complete.return_value = ("ok", 50)

    await use_case.execute(CreateCompletionInput(user_id="u1", prompt="p"))

    saved = repository.save.call_args[0][0]
    assert saved.status == CompletionStatus.SUCCESS
    assert saved.response == "ok"
    assert saved.latency_ms == 50


async def test_execute_on_llm_error_saves_error_completion_and_reraises(use_case, llm_provider, repository):
    llm_provider.complete.side_effect = RuntimeError("LLM down")

    with pytest.raises(RuntimeError, match="LLM down"):
        await use_case.execute(CreateCompletionInput(user_id="u1", prompt="p"))

    saved = repository.save.call_args[0][0]
    assert saved.status == CompletionStatus.ERROR
    assert "LLM down" in saved.error_msg
