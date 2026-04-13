# LLM Gateway

Microsserviço que recebe prompts via HTTP, encaminha para um modelo de linguagem (LLM) e persiste o resultado no banco de dados.

## O que faz

- Recebe um `POST /v1/chat` com `user_id` e `prompt`
- Envia o prompt para um LLM via [LiteLLM](https://github.com/BerriAI/litellm) (Gemini por padrão)
- Persiste a completion (prompt, resposta, status, latência) no PostgreSQL
- Em caso de falha no LLM, persiste o erro antes de retornar o status HTTP correspondente
- Retry automático com backoff exponencial em falhas transitórias

## Arquitetura

O projeto segue **Clean Architecture**, com dependências apontando sempre para dentro:

```
domain/          → entidades e value objects puros, sem dependências externas
application/     → use cases e ports (interfaces abstratas)
infrastructure/  → implementações concretas (PostgreSQL, LiteLLM)
interfaces/      → camada HTTP (FastAPI routers e schemas)
```

A inversão de dependência é aplicada via ABCs em `application/ports/`, permitindo que o use case não conheça nem o banco nem o provedor de LLM.

## Stack

| Categoria       | Lib                  |
|-----------------|----------------------|
| Framework HTTP  | FastAPI              |
| LLM routing     | LiteLLM              |
| Banco de dados  | PostgreSQL + asyncpg |
| ORM             | SQLAlchemy (async)   |
| Migrações       | Alembic              |
| Configuração    | Pydantic Settings    |
| Retry           | Tenacity             |
| Testes          | pytest + pytest-asyncio + httpx |
| Package manager | uv                   |

## Como rodar

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e Docker Compose
- Chave de API do Gemini (ou outro provedor suportado pelo LiteLLM)

### 1. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` e preencha `GEMINI_API_KEY` com sua chave.

### 2. Subir a aplicação

```bash
docker compose up --build
```

Isso sobe o banco PostgreSQL, executa as migrações via Alembic e inicia a API na porta `8000`.

### Endpoints

| Método | Rota       | Descrição                         |
|--------|------------|-----------------------------------|
| POST   | /v1/chat   | Envia um prompt e retorna a resposta do LLM |
| GET    | /health    | Health check                      |
| GET    | /docs      | Swagger UI (apenas em desenvolvimento) |

**Exemplo de requisição:**

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-123", "prompt": "Explique o que é Clean Architecture."}'
```

## Como testar

### Instalar dependências de desenvolvimento

```bash
uv sync
```

### Testes unitários e HTTP (sem banco)

```bash
uv run pytest -m "not integration"
```

### Todos os testes (requer PostgreSQL rodando)

```bash
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5434/llm_gateway uv run pytest
```

### Estrutura dos testes

```
tests/
  unit/domain/        → testes da entidade Completion (sem dependências)
  unit/use_cases/     → testes do use case com ports mockados
  http/               → testes da camada HTTP com use case mockado
  integration/        → testes do repositório contra PostgreSQL real
```

### Linter

```bash
uv run ruff check src tests
```
