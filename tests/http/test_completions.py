async def test_create_completion_returns_201_with_correct_body(client, mock_output):
    response = await client.post("/v1/chat", json={"user_id": "user-1", "prompt": "Hello"})
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == str(mock_output.id)
    assert data["user_id"] == mock_output.user_id
    assert data["response"] == mock_output.response
    assert data["model"] == mock_output.model


async def test_llm_error_propagates_http_status_code(client, mock_use_case):
    from fastapi import HTTPException

    mock_use_case.execute.side_effect = HTTPException(status_code=502, detail="LLM unavailable")

    response = await client.post("/v1/chat", json={"user_id": "user-1", "prompt": "Hello"})

    assert response.status_code == 502


async def test_empty_prompt_returns_422(client):
    response = await client.post("/v1/chat", json={"user_id": "user-1", "prompt": ""})
    assert response.status_code == 422


async def test_empty_user_id_returns_422(client):
    response = await client.post("/v1/chat", json={"user_id": "", "prompt": "Hello"})
    assert response.status_code == 422


async def test_missing_body_returns_422(client):
    response = await client.post("/v1/chat", json={})
    assert response.status_code == 422
