from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateCompletionRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=255)
    prompt: str = Field(min_length=1, max_length=32_000)


class CompletionResponse(BaseModel):
    id: UUID
    user_id: str
    prompt: str
    response: str | None
    model: str
    created_at: datetime
