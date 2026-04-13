from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class CreateCompletionInput:
    user_id: str
    prompt: str


@dataclass(frozen=True)
class CreateCompletionOutput:
    id: UUID
    user_id: str
    prompt: str
    response: str | None
    model: str
    created_at: datetime
