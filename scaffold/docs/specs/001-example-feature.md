---
id: SPEC-001
title: Módulo de exemplo (pagamentos)
status: active
version: 3
updated: 2026-07-19
owner: time-pagamentos
supersedes: []
superseded_by: null
canonical: true
---

# SPEC-001 — Módulo de exemplo (pagamentos)

> Esta é uma spec **viva**. Descreva o estado atual desejado, no presente.
> Não narre a história ("antes era X, agora é Y") — isso vai para um ADR.

## Objetivo

Uma frase sobre o que este domínio resolve.

## Comportamento atual (o que deve valer HOJE)

- Persistência: **DynamoDB** (ver decisão em ADR-0002).
- ...

## Fora de escopo

- ...

## Decisões relacionadas

- ADR-0001 — Postgres como storage inicial (superseded)
- ADR-0002 — Troca para DynamoDB (accepted) ← vigente

## Changelog

| Versão | Data       | Mudança                                   |
|--------|------------|-------------------------------------------|
| 3      | 2026-07-19 | Storage passa a DynamoDB (ADR-0002)       |
| 2      | 2026-03-02 | Adiciona idempotência de cobrança         |
| 1      | 2026-01-10 | Versão inicial                            |
