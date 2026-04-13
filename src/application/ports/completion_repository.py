from abc import ABC, abstractmethod

from domain.entities.completion import Completion


class CompletionRepository(ABC):
    @abstractmethod
    async def save(self, completion: Completion) -> None: ...
