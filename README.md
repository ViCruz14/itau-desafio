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

### Todos os testes

```bash
uv run pytest
```

Os testes de integração sobem um container PostgreSQL automaticamente via [testcontainers](https://testcontainers.com/). É necessário apenas que o Docker esteja rodando.

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

## Melhorias identificadas

### Segurança
A API não possui autenticação. Em produção, adicionaria validação de JWT via dependency do FastAPI, protegendo o endpoint de uso não autorizado e prevenindo custos inesperados com o provedor de LLM. Com JWT, o `user_id` passaria a ser extraído do token — deixando de ser um campo obrigatório no body da requisição.

### Resiliência
O retry atual não distingue rate limit (429) de erro de servidor (502). O ideal seria respeitar o header `Retry-After` retornado pelo provedor em caso de 429.

### Qualidade
Cobertura de testes não é medida nem imposta. Adicionaria `pytest-cov` com um threshold mínimo para garantir que regressões de cobertura sejam detectadas no CI.

### Performance
A conexão com o banco é aberta no início de cada request e mantida aberta durante toda a chamada ao LLM, mesmo sem nenhuma query sendo executada. Em cenários de alta concorrência com respostas lentas do LLM, isso pode esgotar o pool de conexões — não por sobrecarga do banco, mas por conexões ociosas presas esperando o LLM. A solução seria abrir a conexão apenas no momento do `save()`, desacoplando o ciclo de vida da sessão do ciclo de vida do request.
