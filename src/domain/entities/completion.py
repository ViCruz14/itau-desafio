from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from domain.value_objects.completion_status import CompletionStatus


@dataclass
class Completion:
    user_id: str
    prompt: str
    model: str
    id: UUID = field(default_factory=uuid4)
    response: str | None = None
    error_msg: str | None = None
    status: CompletionStatus = field(default=CompletionStatus.PENDING)
    latency_ms: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def mark_success(self, response: str, latency_ms: int) -> None:
        self.response = response
        self.latency_ms = latency_ms
        self.status = CompletionStatus.SUCCESS

    def mark_error(self, error_msg: str, latency_ms: int) -> None:
        self.error_msg = error_msg
        self.latency_ms = latency_ms
        self.status = CompletionStatus.ERROR
