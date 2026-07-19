---
id: SPEC-001
title: Example module (payments)
status: active
version: 3
updated: 2026-07-19
owner: payments-team
supersedes: []
superseded_by: null
canonical: true
---

# SPEC-001 - Example module (payments)

> This is a **living** spec. Describe the current desired state, in the
> present tense. Never narrate history ("it was X, now it is Y") - that goes
> into an ADR.

## Purpose

One sentence on what this domain solves.

## Current behavior (what must hold TODAY)

- Persistence: **DynamoDB** (see decision in ADR-0002).
- ...

## Out of scope

- ...

## Related decisions

- ADR-0001 - Postgres as initial storage (superseded)
- ADR-0002 - Switch to DynamoDB (accepted) <- current

## Changelog

| Version | Date       | Change                                  |
|---------|------------|-----------------------------------------|
| 3       | 2026-07-19 | Storage moves to DynamoDB (ADR-0002)    |
| 2       | 2026-03-02 | Adds charge idempotency                 |
| 1       | 2026-01-10 | Initial version                         |
