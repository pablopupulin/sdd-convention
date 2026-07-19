---
id: SPEC-001
title: sdd-convention plugin architecture
status: active
version: 1
updated: 2026-07-19
owner: pablopupulin
supersedes: []
superseded_by: null
canonical: true
---

# SPEC-001 - sdd-convention plugin architecture

> One canonical spec per domain. Present tense only - this file describes what
> the sdd-convention plugin must be TODAY. Rationale and history live in the
> ADRs under docs/decisions/.

## Purpose

sdd-convention is an installable Claude Code plugin that teaches an agent the
three-layer SDD documentation convention (working / spec / decision) and closes
the loop so documentation stays the single source of truth: at the end of any
turn that changed code, it makes the agent update a spec/ADR or explicitly state
that nothing durable changed.

## Current behavior (what must hold TODAY)

### Distribution

1. The repository is simultaneously a marketplace and a plugin: a single public
   repo shipping `.claude-plugin/marketplace.json` (listing the plugin with
   `source: "."`) and `.claude-plugin/plugin.json`. Plugin and marketplace name:
   `sdd-convention`. (ADR-0001)
2. Install path: `/plugin marketplace add pablopupulin/sdd-convention` then
   `/plugin install sdd-convention`.

### Skills (open Agent Skills format: `skills/<name>/SKILL.md`)

3. `sdd-source-of-truth` - defines the 3-layer model, the authority order, the
   frontmatter schemas, and the four lifecycle rules. Triggers when reading or
   editing `docs/specs/`, `docs/decisions/`, `docs/_archive/`, or when
   determining the system's current behavior.
4. `sdd-finalize` - end-of-task checklist that promotes durable knowledge into
   specs/ADRs. It is the skill the Stop hook names when it blocks.
5. `sdd-retrofit` - interactive, approval-gated playbook to migrate an existing
   messy documentation base into the convention.
6. Every skill's frontmatter `description` stays under 1024 characters.

### Commands (`commands/<name>.md` -> `/sdd-convention:<name>`)

7. `/sdd-init` - idempotently copies the scaffold (docs structure +
   `scripts/check-docs.py`), asks the docs language, and merges a
   marker-delimited rules block (`<!-- sdd-convention:start -->` …
   `<!-- sdd-convention:end -->`) into `CLAUDE.md` or `AGENTS.md`.
8. `/sdd-retrofit` - thin wrapper that invokes the `sdd-retrofit` skill.

### Enforcement

9. A Stop hook (`hooks/check-docs-updated.py`, launched by the polyglot
   `hooks/run-hook.cmd`, registered in `hooks/hooks.json`) blocks the stop of a
   turn ONLY when that turn edited project files outside `docs/` without also
   editing `docs/specs/` or `docs/decisions/`. It blocks by printing
   `{"decision": "block", "reason": ...}` on stdout with exit 0. (ADR-0002)
10. The hook is opt-in per project (silent exit 0 when the project has no
    `docs/specs/`) and anti-loop (silent when `stop_hook_active` is true).
    "Current turn" = everything after the last real user prompt in the
    transcript.
11. The hook fails open: any unexpected condition (no Python, malformed input,
    unreadable transcript) exits 0 with no output. Hard enforcement lives in CI
    via `check-docs.py`, not in the hook. (ADR-0002, ADR-0004)
12. The hook launcher is a single polyglot `.cmd` file (cmd.exe batch + POSIX
    sh) so it runs on Windows and POSIX; hook commands never reference `.sh`
    files. (ADR-0003)

### Assets and tooling

13. `scaffold/` ships the `docs/` structure + `scripts/check-docs.py` that
    `/sdd-init` copies. `templates/` ships `spec.md` and `adr.md` with ready
    frontmatter.
14. `check-docs.py` and the Stop hook use the Python 3 standard library only;
    pytest is a development/CI dependency only. (ADR-0004)
15. CI (`.github/workflows/ci.yml`) runs the hook's pytest suite and
    `check-docs.py` on Ubuntu and Windows.

### Content language

16. All plugin content (skills, commands, scaffold, README) is in English. Docs
    generated in a target project follow that project's language, but frontmatter
    keys and status values stay in English (the linter depends on them).

### Other agents

17. Skills use the open Agent Skills format so other agents (Codex, Cursor, …)
    can consume them; the README ships an `AGENTS.md` snippet with the authority
    order, the four rules, and the finalize instruction. Hooks are Claude
    Code-only; elsewhere enforcement is instructional.

## Out of scope

- RAG / Obsidian integration.
- A PreToolUse hook on `git commit` (only the Stop hook is used). (ADR-0002)
- Publishing to third-party marketplaces.
- Documentation formats other than Markdown with YAML frontmatter.

## Related decisions

- ADR-0001 - Repo is both marketplace and plugin (accepted)
- ADR-0002 - Enforce doc updates via a fail-open Stop hook (accepted)
- ADR-0003 - Windows-compatible polyglot .cmd hook launcher (accepted)
- ADR-0004 - Python standard library only for hook and linter (accepted)

## Changelog

| Version | Date       | Change                                             |
|---------|------------|----------------------------------------------------|
| 1       | 2026-07-19 | Initial spec, retrofit from the brainstorm design. |
