# Decisions (ADRs - the immutable "why" log)

This is where **legitimate contradictions** live. When the system changes
from A to B, the "A" does not linger in a spec pretending to be current: it
becomes an ADR marked `superseded`, and a new ADR (`supersedes: ...`) records
the B.

Format: lean [MADR](https://adr.github.io/madr/). Rules:

- **Append-only.** Never edit an accepted ADR's decision; never delete.
- Changed your mind? Write a **new** ADR and mark the old one `superseded`,
  linking both via `supersedes` / `superseded_by`.
- Sequential 4-digit numbering: `0001`, `0002`, ...

## Decision log

| ADR      | Title                                            | Status   | Supersedes | Date       |
|----------|--------------------------------------------------|----------|------------|------------|
| ADR-0001 | Repo is both marketplace and plugin              | accepted | -          | 2026-07-19 |
| ADR-0002 | Enforce doc updates via a fail-open Stop hook     | accepted | -          | 2026-07-19 |
| ADR-0003 | Windows-compatible polyglot .cmd hook launcher   | accepted | -          | 2026-07-19 |
| ADR-0004 | Python standard library only for hook and linter | accepted | -          | 2026-07-19 |
| ADR-0005 | Ecosystems are adapter data; Decision layer fixed | accepted | -          | 2026-07-19 |

## Required frontmatter

```yaml
---
id: ADR-0002
title: Switch persistence to DynamoDB
status: accepted      # proposed | accepted | superseded | deprecated | rejected
date: 2026-07-19
supersedes: ADR-0001  # or null
superseded_by: null   # filled when another ADR replaces this one
---
```
