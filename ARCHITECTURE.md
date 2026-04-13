# Arquitetura Cloud Native — LLM Gateway

## Visão geral

```
Internet
    │
    ▼
API Gateway
    │
    ▼
ECS Fargate  (auto scaling)
    │                   │
    ▼                   ▼
RDS PostgreSQL     LLM Provider
(multi-AZ)         (Gemini / OpenRouter)
```

---

## 1. Escalabilidade

**ECS Fargate** com auto scaling baseado no número de requisições — escala horizontalmente conforme a demanda. Como a aplicação é assíncrona (FastAPI + asyncio), cada container suporta muitas requisições simultâneas, então o scaling não precisa ser agressivo.

**API Gateway** como entry point: oferece throttling, rate limiting e autenticação JWT nativamente. O timeout máximo de 29s é compatível com a aplicação — o `LLM_TIMEOUT_SECONDS` deve ser configurado abaixo desse valor (ex: 25s).

---

## 2. Observabilidade

- **Logs** — CloudWatch Logs via ECS, em JSON estruturado com `user_id`, `model`, `latency_ms` e `status`
- **Métricas** — CloudWatch Metrics com taxa de erro e latência das chamadas ao LLM
- **Alertas** — CloudWatch Alarms → SNS → Slack em error rate acima de 5% ou latência p99 acima de 25s

---

## 3. Banco de dados

**PostgreSQL** é a escolha natural: o dado é relacional (completions por usuário, com status e timestamps), o schema é versionado com Alembic e queries por `user_id` ou período são simples com índices. RDS gerenciado elimina overhead operacional de manutenção e backups.

---

## 4. Resiliência a falhas

**Falha do LLM** — dependência mais crítica e mais propensa a instabilidade:
- Retry com backoff exponencial já está implementado via Tenacity
- Fallback de provedor: LiteLLM suporta múltiplos provedores nativamente — Gemini como primário e OpenRouter como fallback, transparente para a aplicação

**Falha do banco** — RDS Multi-AZ realiza failover automático sem intervenção manual

**Falha da aplicação** — ECS substitui tasks com falha automaticamente; o health check do ALB em `/health` remove instâncias unhealthy do balanceamento antes da substituição
