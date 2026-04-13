from application.dtos.completion_dto import CreateCompletionInput, CreateCompletionOutput
from application.ports.completion_repository import CompletionRepository
from application.ports.llm_provider import LLMProvider
from domain.entities.completion import Completion


class CreateCompletion:
    def __init__(
        self,
        llm_provider: LLMProvider,
        completion_repository: CompletionRepository,
        model: str,
    ) -> None:
        self._llm_provider = llm_provider
        self._repository = completion_repository
        self._model = model

    async def execute(self, input_dto: CreateCompletionInput) -> CreateCompletionOutput:
        completion = Completion(
            user_id=input_dto.user_id,
            prompt=input_dto.prompt,
            model=self._model,
        )

        try:
            response, latency_ms = await self._llm_provider.complete(input_dto.prompt, self._model)
            completion.mark_success(response, latency_ms)
            await self._repository.save(completion)
        except Exception as exc:
            completion.mark_error(str(exc), 0)
            await self._repository.save(completion)
            raise

        return CreateCompletionOutput(
            id=completion.id,
            user_id=completion.user_id,
            prompt=completion.prompt,
            response=completion.response,
            model=completion.model,
            created_at=completion.created_at,
        )
