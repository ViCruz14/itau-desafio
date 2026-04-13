from sqlalchemy.ext.asyncio import AsyncSession

from application.ports.completion_repository import CompletionRepository
from domain.entities.completion import Completion
from infrastructure.database.models.completion_model import CompletionModel


class PgCompletionRepository(CompletionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, completion: Completion) -> None:
        self._session.add(self._to_model(completion))
        await self._session.commit()

    def _to_model(self, e: Completion) -> CompletionModel:
        return CompletionModel(
            id=e.id,
            user_id=e.user_id,
            prompt=e.prompt,
            response=e.response,
            model=e.model,
            status=e.status.value,
            error_msg=e.error_msg,
            latency_ms=e.latency_ms,
            created_at=e.created_at,
        )
