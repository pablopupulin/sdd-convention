---
id: ADR-0002
title: Trocar persistência para DynamoDB
status: accepted
date: 2026-07-19
supersedes: ADR-0001
superseded_by: null
---

# ADR-0002 — Trocar persistência para DynamoDB

## Contexto

O volume de escrita cresceu e a escala horizontal do Postgres virou gargalo
operacional. Este é exatamente o caso "antes era A, agora é B": ADR-0001 dizia
Postgres; esta decisão o substitui.

## Decisão

Migrar a persistência do módulo de pagamentos para DynamoDB.

## Consequências

- Escala horizontal e latência previsível.
- Perde transações multi-item nativas → idempotência tratada na aplicação.
- **Ação obrigatória:** SPEC-001 foi atualizada (v3) para refletir DynamoDB, e
  ADR-0001 foi marcado `superseded`.

## Relacionado

- Supersede: ADR-0001
- Reflete em: SPEC-001 (v3)
