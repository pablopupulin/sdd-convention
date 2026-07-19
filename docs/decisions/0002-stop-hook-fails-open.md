---
id: ADR-0002
title: Enforce doc updates via a fail-open Stop hook
status: accepted
date: 2026-07-19
supersedes: null
superseded_by: null
---

# ADR-0002 - Enforce doc updates via a fail-open Stop hook

## Context

The convention only works if agents actually update docs when they change code.
Enforcement could be a PreToolUse gate on `git commit`, an end-of-turn Stop
hook, or purely instructional. Whatever it is, it must not break sessions when
it misfires or when its dependencies are missing.

## Decision

Enforce at end of turn with a Stop hook (`check-docs-updated.py`) paired with the
`sdd-finalize` skill: the hook is the deterministic reminder, the skill carries
the judgment. The hook blocks only when the current turn edited files outside
`docs/` without touching `docs/specs/` or `docs/decisions/`, and it fails open
(exit 0, no output) on any unexpected condition. Hard enforcement lives in CI via
`check-docs.py`. We explicitly reject a PreToolUse hook on `git commit`.

## Consequences

- A misfiring or dependency-less hook never blocks the user; enforcement
  degrades gracefully to the skill layer and CI.
- Any file outside `docs/` counts as "code" - a deliberately simple rule; false
  positives are cheap because the legitimate exit is one sentence stating that
  nothing durable changed.
- The block reason names the `sdd-finalize` skill, coupling the hook's text to
  that skill's directory name.
