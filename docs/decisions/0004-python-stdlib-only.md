---
id: ADR-0004
title: Python standard library only for hook and linter
status: accepted
date: 2026-07-19
supersedes: null
superseded_by: null
---

# ADR-0004 - Python standard library only for hook and linter

## Context

The Stop hook (`check-docs-updated.py`) and the hygiene linter
(`scaffold/scripts/check-docs.py`) run in arbitrary user projects and in the
plugin's own CI. Requiring third-party packages (for example a YAML parser)
would add an install step and a failure mode in every environment they touch.

## Decision

Implement both scripts with the Python 3 standard library only, including a
minimal hand-rolled parser for the "flat" YAML frontmatter the convention uses.
pytest is allowed as a development/CI dependency only.

## Consequences

- The hook and linter run anywhere Python 3 is present, with no `pip install`.
- The frontmatter parser supports only flat `key: value` and simple `[a, b]`
  lists - nested YAML is intentionally unsupported.
- Test tooling (pytest) stays out of the runtime path.
