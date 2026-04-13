import asyncio
import time

import litellm
from fastapi import HTTPException
from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from application.ports.llm_provider import LLMProvider
from config.settings import Settings

litellm.suppress_debug_info = True


class LiteLLMProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        self._timeout = settings.llm_timeout_seconds
        self._max_retries = settings.llm_max_retries

    async def complete(self, prompt: str, model: str) -> tuple[str, int]:
        @retry(
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(min=1, max=8),
            retry=retry_if_not_exception_type(HTTPException),
            reraise=True,
        )
        async def _call() -> tuple[str, int]:
            start = time.monotonic()
            try:
                response = await asyncio.wait_for(
                    litellm.acompletion(
                        model=model, messages=[{"role": "user", "content": prompt}]
                    ),
                    timeout=self._timeout,
                )
                latency_ms = int((time.monotonic() - start) * 1000)
                return response.choices[0].message.content, latency_ms
            except asyncio.TimeoutError:
                raise HTTPException(
                    status_code=504, detail=f"LLM timed out after {self._timeout}s."
                )
            except Exception as exc:
                raise HTTPException(status_code=502, detail=str(exc))

        return await _call()
