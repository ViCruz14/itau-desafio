from fastapi import APIRouter, Depends, status

from application.dtos.completion_dto import CreateCompletionInput
from application.use_cases.create_completion import CreateCompletion
from container import get_create_completion_use_case
from interfaces.http.schemas.completion_schema import (
    CompletionResponse,
    CreateCompletionRequest,
)

router = APIRouter(prefix="/v1/chat", tags=["chat"])


@router.post("", response_model=CompletionResponse, status_code=status.HTTP_201_CREATED)
async def create_completion(
    body: CreateCompletionRequest,
    use_case: CreateCompletion = Depends(get_create_completion_use_case),
) -> CompletionResponse:
    output = await use_case.execute(
        CreateCompletionInput(user_id=body.user_id, prompt=body.prompt)
    )
    return CompletionResponse.model_validate(output, from_attributes=True)
