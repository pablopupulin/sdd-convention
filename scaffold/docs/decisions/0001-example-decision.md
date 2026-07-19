---
id: ADR-0001
title: Postgres como storage inicial
status: superseded
date: 2026-01-10
supersedes: null
superseded_by: ADR-0002
---

# ADR-0001 — Postgres como storage inicial

> STATUS: **superseded por ADR-0002**. Mantido para histórico. Não é vigente.

## Contexto

No início do projeto precisávamos de um storage relacional simples, com
transações fortes e familiaridade do time.

## Decisão

Usar PostgreSQL como banco primário do módulo de pagamentos.

## Consequências

- Transações ACID prontas.
- Acoplamento ao modelo relacional (custo alto de escala horizontal — foi o que
  motivou o ADR-0002).
