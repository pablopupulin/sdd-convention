---
id: ADR-0003
title: Windows-compatible polyglot .cmd hook launcher
status: accepted
date: 2026-07-19
supersedes: null
superseded_by: null
---

# ADR-0003 - Windows-compatible polyglot .cmd hook launcher

## Context

Claude Code runs the Stop hook command on both Windows and POSIX. Referencing a
`.sh` file in the hook command gets mangled by Claude Code's Windows
auto-detection, and a Python entrypoint still needs an OS-appropriate launcher.

## Decision

Launch the hook through a single polyglot `hooks/run-hook.cmd` that is valid both
as a cmd.exe batch script and as a POSIX sh script (the same pattern Superpowers
uses). It locates Python (`py` / `python` on Windows, `python3` / `python` on
POSIX) and fails open (exit 0) when none is found. Hook commands never reference
`.sh` files.

## Consequences

- One launcher works on Windows and POSIX with no per-OS hook configuration.
- Missing Python degrades to a silent no-op instead of an error.
- Contributors must keep both halves of the polyglot file in sync.
