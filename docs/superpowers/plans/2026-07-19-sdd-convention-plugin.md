# sdd-convention Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform this repo into an installable Claude Code plugin (repo = marketplace + plugin) that enforces the SDD documentation convention: 3 modular skills, `/sdd-init` and `/sdd-retrofit` commands, a fail-open Python Stop hook with tests, English content, published to `github.com/pablopupulin/sdd-convention`.

**Architecture:** Single public GitHub repo that is both marketplace and plugin (`.claude-plugin/marketplace.json` with `source: "."`). Skills follow the open Agent Skills format (`skills/<name>/SKILL.md`) for portability to other agents. Enforcement is a Stop hook (deterministic reminder) paired with the `sdd-finalize` skill (judgment); hard enforcement lives in CI via `check-docs.py`.

**Tech Stack:** Claude Code plugin system (plugin.json / marketplace.json / hooks.json / commands / skills), Python 3 stdlib only (hook + linter), pytest (tests), GitHub Actions (CI), gh CLI (publication).

## Global Constraints

- All plugin content (skills, commands, scaffold, README) in **English**. Generated docs in target projects follow the target project's language.
- Python: **stdlib only** for `hooks/check-docs-updated.py` and `scaffold/scripts/check-docs.py`. pytest is a dev/CI dependency only.
- The Stop hook **fails open**: any unexpected condition (no Python, malformed input, unreadable transcript) → exit 0, no output. It always exits 0; blocking is signaled only via `{"decision": "block", "reason": ...}` on stdout.
- Plugin name: `sdd-convention`. Marketplace name: `sdd-convention`. Version: `0.1.0` (plugin.json, marketplace.json, git tag `v0.1.0`).
- Repo: `pablopupulin/sdd-convention`, public. License: MIT.
- Skill frontmatter `description` must stay under 1024 characters.
- Frontmatter keys and status values (`active`, `superseded`, `archived`, etc.) are always English — the linter depends on them — even when a project's docs are in another language.
- Windows-compatible: hook launcher is a polyglot `.cmd` (cmd.exe batch + POSIX sh in one file, same pattern Superpowers uses). Never reference `.sh` files in hook commands (Claude Code's Windows auto-detection mangles them).
- Existing working docs (`docs/superpowers/specs/`, `docs/superpowers/plans/`) stay in the repo.
- Each task ends with a commit; commit messages end with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

## Verified facts (do not re-research)

- `plugin.json` fields: `name` (required), `version`, `description`, `author {name, email}`, `homepage`, `repository`, `license`, `keywords`. Location: `.claude-plugin/plugin.json`.
- `marketplace.json` fields: `name`, `owner {name}`, `plugins: [{name, source: ".", description, version}]`. Location: `.claude-plugin/marketplace.json`.
- Hooks live in `hooks/hooks.json`; `${CLAUDE_PLUGIN_ROOT}` expands to the plugin install dir; `Stop` hooks take no matcher; `timeout` is in seconds.
- Stop hook stdin JSON includes `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `stop_hook_active` (true when already continuing due to a Stop-hook block — this is the anti-loop). Block by printing `{"decision": "block", "reason": "..."}` to stdout with exit 0.
- Transcript at `transcript_path` is JSONL. Real user prompts: `{"type":"user","message":{"role":"user","content":"<string>"}}` (tool results are also `type:"user"` but content is a list containing `{"type":"tool_result",...}` blocks). Assistant tool calls: `{"type":"assistant"...,"message":{"role":"assistant","content":[{"type":"tool_use","name":"Edit","input":{"file_path":"..."}}]}}`. Other line types (`queue-operation`, `file-history-snapshot`, `attachment`, `ai-title`, `last-prompt`) must be skipped leniently.
- Plugin commands: `commands/<name>.md` with frontmatter `description`, optional `argument-hint`; installed as `/sdd-convention:<name>` (short form `/<name>` when unambiguous).
- Skills: `skills/<dir-name>/SKILL.md`, frontmatter `name` + `description`; extra files in the skill dir are auto-available.
- CLI validation/testing: `claude plugin validate .`, `claude plugin marketplace add <path-or-owner/repo>`, `claude plugin install <plugin>@<marketplace>`.

## File Structure (final state)

```
sdd-convention/
├── .claude-plugin/
│   ├── plugin.json              # Task 1
│   └── marketplace.json         # Task 1
├── .github/workflows/ci.yml     # Task 10
├── .gitignore                   # Task 1
├── LICENSE                      # Task 1
├── hooks/
│   ├── hooks.json               # Task 2
│   ├── run-hook.cmd             # Task 2 (polyglot launcher)
│   └── check-docs-updated.py    # Task 2 (the Stop hook)
├── tests/
│   └── test_check_docs_updated.py  # Task 2
├── templates/
│   ├── spec.md                  # Task 3
│   └── adr.md                   # Task 3
├── skills/
│   ├── sdd-source-of-truth/SKILL.md  # Task 4
│   ├── sdd-finalize/SKILL.md         # Task 5
│   └── sdd-retrofit/SKILL.md         # Task 6
├── commands/
│   ├── sdd-init.md              # Task 7
│   └── sdd-retrofit.md          # Task 7
├── scaffold/                    # Task 8 (rewritten in English)
│   ├── CLAUDE.md                #   with <!-- sdd-convention:start/end --> markers
│   ├── docs/{specs,decisions,plans,_archive}/...
│   └── scripts/check-docs.py
├── docs/superpowers/{specs,plans}/   # existing working docs (keep)
└── README.md                    # Task 9 (rewritten in English)
```

---

### Task 1: Plugin manifests, license, gitignore

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`
- Create: `.gitignore`
- Create: `LICENSE`

**Interfaces:**
- Produces: plugin name `sdd-convention` and marketplace name `sdd-convention`, version `0.1.0` — Tasks 10 and 11 rely on these exact names for `claude plugin validate` / install commands.

- [ ] **Step 1: Write `.claude-plugin/plugin.json`**

```json
{
  "name": "sdd-convention",
  "description": "Spec-driven development with a single source of truth: living specs, append-only ADRs, disposable plans - plus a Stop hook that reminds agents to update docs before finishing",
  "version": "0.1.0",
  "author": {
    "name": "Pablo Pupulin",
    "email": "pablopupulin@gmail.com"
  },
  "homepage": "https://github.com/pablopupulin/sdd-convention",
  "repository": "https://github.com/pablopupulin/sdd-convention",
  "license": "MIT",
  "keywords": [
    "sdd",
    "spec-driven-development",
    "documentation",
    "adr",
    "source-of-truth",
    "skills"
  ]
}
```

- [ ] **Step 2: Write `.claude-plugin/marketplace.json`**

```json
{
  "name": "sdd-convention",
  "description": "Marketplace for the sdd-convention plugin",
  "owner": {
    "name": "Pablo Pupulin",
    "email": "pablopupulin@gmail.com"
  },
  "plugins": [
    {
      "name": "sdd-convention",
      "description": "Spec-driven development with a single source of truth: living specs, append-only ADRs, disposable plans - plus a Stop hook that reminds agents to update docs before finishing",
      "version": "0.1.0",
      "source": ".",
      "author": {
        "name": "Pablo Pupulin",
        "email": "pablopupulin@gmail.com"
      }
    }
  ]
}
```

- [ ] **Step 3: Write `.gitignore`**

```
__pycache__/
*.pyc
.pytest_cache/
```

- [ ] **Step 4: Write `LICENSE`** (MIT, standard text)

```
MIT License

Copyright (c) 2026 Pablo Pupulin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 5: Validate JSON syntax**

Run: `python -m json.tool .claude-plugin/plugin.json && python -m json.tool .claude-plugin/marketplace.json`
Expected: both print the parsed JSON, exit 0.

- [ ] **Step 6: Commit**

```bash
git add .claude-plugin .gitignore LICENSE
git commit -m "feat: add plugin and marketplace manifests

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Stop hook (TDD)

**Files:**
- Test: `tests/test_check_docs_updated.py`
- Create: `hooks/check-docs-updated.py`
- Create: `hooks/run-hook.cmd`
- Create: `hooks/hooks.json`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: the block `reason` string mentions the skill name `sdd-finalize` — Task 5 must create a skill with exactly that directory name. `hooks/hooks.json` references `${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd`.

Behavior under test (from the design spec): the hook reads the hook JSON on stdin and blocks the stop **only when** the current turn edited files inside the project but outside `docs/`, without also editing `docs/specs/` or `docs/decisions/`. It exits 0 silently when: the project has no `docs/specs/` dir; `stop_hook_active` is true; no edits happened; docs were updated; edits were outside the project (scratchpad); input or transcript is malformed. "Current turn" = everything after the last real user prompt in the transcript.

- [ ] **Step 1: Write the failing tests — full content of `tests/test_check_docs_updated.py`**

```python
"""End-to-end tests for hooks/check-docs-updated.py (sdd-convention Stop hook).

The hook is exercised as a subprocess exactly as Claude Code runs it:
hook JSON on stdin, optional {"decision": "block"} JSON on stdout, exit 0.
"""
import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "check-docs-updated.py"
WRAPPER = Path(__file__).resolve().parent.parent / "hooks" / "run-hook.cmd"


# --- transcript line builders -------------------------------------------------

def user_line(text="please do the thing"):
    return {"type": "user", "message": {"role": "user", "content": text}}


def tool_result_line():
    return {
        "type": "user",
        "message": {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": "ok"}
            ],
        },
    }


def edit_line(path, tool="Edit"):
    key = "notebook_path" if tool == "NotebookEdit" else "file_path"
    return {
        "type": "assistant",
        "message": {
            "role": "assistant",
            "content": [
                {"type": "tool_use", "id": "t1", "name": tool, "input": {key: str(path)}}
            ],
        },
    }


def noise_lines():
    """Non-message line types that appear in real transcripts."""
    return [
        {"type": "queue-operation", "operation": "enqueue"},
        {"type": "file-history-snapshot", "messageId": "m1"},
        {"type": "ai-title", "aiTitle": "Some title"},
        {"type": "last-prompt", "lastPrompt": "..."},
    ]


# --- harness ------------------------------------------------------------------

def write_transcript(tmp_path, entries, extra_raw_lines=()):
    p = tmp_path / "transcript.jsonl"
    lines = [json.dumps(e) for e in entries]
    lines.extend(extra_raw_lines)
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


def make_project(tmp_path, with_specs=True):
    project = tmp_path / "project"
    if with_specs:
        (project / "docs" / "specs").mkdir(parents=True)
    else:
        project.mkdir()
    return project


def run_hook(project, transcript, stop_hook_active=False, executable=None):
    payload = {
        "session_id": "s1",
        "hook_event_name": "Stop",
        "cwd": str(project),
        "transcript_path": str(transcript),
        "stop_hook_active": stop_hook_active,
    }
    if executable is None:
        cmd = [sys.executable, str(HOOK)]
    else:
        cmd = executable
    result = subprocess.run(
        cmd,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"exit={result.returncode} stderr={result.stderr}"
    return result.stdout.strip()


def assert_blocks(out):
    decision = json.loads(out)
    assert decision["decision"] == "block"
    assert "sdd-finalize" in decision["reason"]


# --- scenarios ----------------------------------------------------------------

def test_blocks_when_code_edited_without_docs(tmp_path):
    project = make_project(tmp_path)
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "src" / "main.py"),
    ])
    assert_blocks(run_hook(project, transcript))


def test_passes_when_spec_also_edited(tmp_path):
    project = make_project(tmp_path)
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "src" / "main.py"),
        edit_line(project / "docs" / "specs" / "001-payments.md"),
    ])
    assert run_hook(project, transcript) == ""


def test_passes_when_adr_also_edited(tmp_path):
    project = make_project(tmp_path)
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "src" / "main.py", tool="Write"),
        edit_line(project / "docs" / "decisions" / "0003-switch.md", tool="Write"),
    ])
    assert run_hook(project, transcript) == ""


def test_plans_edit_does_not_satisfy_docs_requirement(tmp_path):
    # docs/plans/ is the ephemeral layer - editing it is not a durable update
    project = make_project(tmp_path)
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "src" / "main.py"),
        edit_line(project / "docs" / "plans" / "active" / "plan.md"),
    ])
    assert_blocks(run_hook(project, transcript))


def test_docs_only_edit_passes(tmp_path):
    # editing only docs/ (even plans) never triggers the reminder
    project = make_project(tmp_path)
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "docs" / "plans" / "active" / "plan.md"),
    ])
    assert run_hook(project, transcript) == ""


def test_passes_when_no_edits(tmp_path):
    project = make_project(tmp_path)
    transcript = write_transcript(tmp_path, [user_line()])
    assert run_hook(project, transcript) == ""


def test_passes_when_stop_hook_active(tmp_path):
    project = make_project(tmp_path)
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "src" / "main.py"),
    ])
    assert run_hook(project, transcript, stop_hook_active=True) == ""


def test_passes_when_project_has_no_docs_specs(tmp_path):
    project = make_project(tmp_path, with_specs=False)
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "src" / "main.py"),
    ])
    assert run_hook(project, transcript) == ""


def test_ignores_edits_outside_project(tmp_path):
    # scratchpad / other-repo writes must not trigger the reminder
    project = make_project(tmp_path)
    outside = tmp_path / "scratchpad" / "notes.py"
    transcript = write_transcript(tmp_path, [user_line(), edit_line(outside)])
    assert run_hook(project, transcript) == ""


def test_only_current_turn_counts(tmp_path):
    # a code edit in a PREVIOUS turn must not trigger on a question-only turn
    project = make_project(tmp_path)
    transcript = write_transcript(tmp_path, [
        user_line("first task"),
        edit_line(project / "src" / "a.py"),
        user_line("now just answer a question"),
    ])
    assert run_hook(project, transcript) == ""


def test_tool_result_lines_do_not_start_a_new_turn(tmp_path):
    # tool_result entries are type:"user" but must NOT reset the turn boundary
    project = make_project(tmp_path)
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "src" / "a.py"),
        tool_result_line(),
    ])
    assert_blocks(run_hook(project, transcript))


def test_notebook_edit_counts_as_code_edit(tmp_path):
    project = make_project(tmp_path)
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "analysis" / "nb.ipynb", tool="NotebookEdit"),
    ])
    assert_blocks(run_hook(project, transcript))


def test_noise_and_malformed_lines_are_skipped(tmp_path):
    project = make_project(tmp_path)
    transcript = write_transcript(
        tmp_path,
        noise_lines() + [user_line(), edit_line(project / "src" / "main.py")],
        extra_raw_lines=["not json at all {{{", ""],
    )
    assert_blocks(run_hook(project, transcript))


def test_malformed_stdin_fails_open(tmp_path):
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input="this is not json",
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_missing_transcript_fails_open(tmp_path):
    project = make_project(tmp_path)
    missing = tmp_path / "nope.jsonl"
    assert run_hook(project, missing) == ""


def test_wrapper_launcher_blocks_end_to_end(tmp_path):
    """Run the polyglot run-hook.cmd the way Claude Code would on this OS."""
    project = make_project(tmp_path)
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "src" / "main.py"),
    ])
    if sys.platform == "win32":
        cmd = ["cmd.exe", "/c", str(WRAPPER)]
    else:
        cmd = ["sh", str(WRAPPER)]
    assert_blocks(run_hook(project, transcript, executable=cmd))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pip install pytest` (if not installed), then `python -m pytest tests/ -v`
Expected: ALL tests FAIL or ERROR (hook script does not exist yet → `FileNotFoundError` / non-zero exit assertions).

- [ ] **Step 3: Write `hooks/check-docs-updated.py` — full content**

```python
#!/usr/bin/env python3
"""Stop hook for the sdd-convention plugin.

Reminds the agent to update durable docs (specs/ADRs) when a turn edited
project files outside docs/ without touching docs/specs/ or docs/decisions/.

Fail-open by design: any unexpected condition exits 0 with no output. The
hook is a deterministic reminder, not a gate - hard enforcement lives in CI
(scaffold/scripts/check-docs.py).

stdin:  Claude Code hook JSON (transcript_path, cwd, stop_hook_active, ...).
stdout: {"decision": "block", "reason": "..."} when the reminder fires.
exit:   always 0.
"""
import json
import os
import sys

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}

REASON = (
    "SDD convention check: this turn edited project files outside docs/ but did "
    "not update docs/specs/ or docs/decisions/. Invoke the sdd-finalize skill "
    "now and either (a) update the canonical spec and/or write an ADR for what "
    "changed, or (b) if nothing durable changed (pure refactor, typo, tooling), "
    "state that explicitly to the user in one sentence. Do not fabricate doc "
    "updates."
)


def is_real_user_prompt(entry):
    """True for transcript lines that start a turn: a user message whose
    content is plain text. Tool results also have type "user" but their
    content is a list of tool_result blocks."""
    if entry.get("type") != "user" or entry.get("isSidechain"):
        return False
    message = entry.get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return True
    if isinstance(content, list):
        kinds = {b.get("type") for b in content if isinstance(b, dict)}
        return "text" in kinds and "tool_result" not in kinds
    return False


def edited_paths_in_last_turn(transcript_path):
    entries = []
    with open(transcript_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(entry, dict):
                entries.append(entry)

    turn_start = 0
    for i, entry in enumerate(entries):
        if is_real_user_prompt(entry):
            turn_start = i

    paths = []
    for entry in entries[turn_start:]:
        if entry.get("isSidechain"):
            continue
        message = entry.get("message") or {}
        if message.get("role") != "assistant":
            continue
        for block in message.get("content") or []:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            if block.get("name") not in EDIT_TOOLS:
                continue
            tool_input = block.get("input") or {}
            path = tool_input.get("file_path") or tool_input.get("notebook_path")
            if path:
                paths.append(path)
    return paths


def project_relative(path, cwd):
    """Path relative to cwd with forward slashes, or None when the path lies
    outside the project (scratchpads, other repos, other drives)."""
    try:
        rel = os.path.relpath(
            os.path.normcase(os.path.normpath(path)),
            os.path.normcase(os.path.normpath(cwd)),
        )
    except ValueError:
        return None
    rel = rel.replace(os.sep, "/")
    if rel == "." or rel.startswith("../"):
        return None
    return rel


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(data, dict) or data.get("stop_hook_active"):
        return 0

    cwd = data.get("cwd") or os.getcwd()
    if not os.path.isdir(os.path.join(cwd, "docs", "specs")):
        return 0  # project has not opted into the convention

    transcript_path = data.get("transcript_path")
    if not transcript_path or not os.path.isfile(transcript_path):
        return 0

    try:
        edited = edited_paths_in_last_turn(transcript_path)
    except OSError:
        return 0

    rels = [r for r in (project_relative(p, cwd) for p in edited) if r]
    code_edits = [r for r in rels if not r.startswith("docs/")]
    doc_edits = [
        r for r in rels
        if r.startswith("docs/specs/") or r.startswith("docs/decisions/")
    ]

    if code_edits and not doc_edits:
        print(json.dumps({"decision": "block", "reason": REASON}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Write `hooks/run-hook.cmd` — polyglot launcher, full content**

```
: << 'CMDBLOCK'
@echo off
REM Polyglot launcher for the sdd-convention Stop hook.
REM On Windows cmd.exe runs this batch block; POSIX shells skip it (the first
REM line is a no-op heredoc in sh). Fails open (exit 0) when no Python is
REM available: the hook is a reminder, not a gate - CI carries enforcement.
where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    py -3 "%~dp0check-docs-updated.py"
    exit /b 0
)
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python "%~dp0check-docs-updated.py"
    exit /b 0
)
exit /b 0
CMDBLOCK

# POSIX: prefer python3, fall back to python, else fail open.
DIR="$(cd "$(dirname "$0")" && pwd)"
if command -v python3 >/dev/null 2>&1; then exec python3 "$DIR/check-docs-updated.py"; fi
if command -v python >/dev/null 2>&1; then exec python "$DIR/check-docs-updated.py"; fi
exit 0
```

- [ ] **Step 5: Write `hooks/hooks.json`**

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\"",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `python -m pytest tests/ -v`
Expected: all 16 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add tests/test_check_docs_updated.py hooks/
git commit -m "feat: add Stop hook that reminds agents to update specs/ADRs

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Templates

**Files:**
- Create: `templates/spec.md`
- Create: `templates/adr.md`

**Interfaces:**
- Produces: template paths `templates/spec.md` and `templates/adr.md` — the skills (Tasks 4-6) reference these exact paths as `${CLAUDE_PLUGIN_ROOT}/templates/...`.

- [ ] **Step 1: Write `templates/spec.md`**

```markdown
---
id: SPEC-XXX
title: <Domain name>
status: draft         # draft | active | superseded | archived
version: 1
updated: YYYY-MM-DD
owner: <team-or-person>
supersedes: []
superseded_by: null
canonical: true
---

# SPEC-XXX - <Domain name>

> One canonical spec per domain. Present tense only - this file describes what
> must hold TODAY. History and rationale live in ADRs (docs/decisions/).

## Purpose

<One sentence on what this domain solves.>

## Current behavior (what must hold TODAY)

<Numbered requirements work well. No "previously X" narration - ever.>

## Out of scope

<What this domain explicitly does not cover.>

## Related decisions

<ADR-XXXX - title (status). List the ADRs that shaped this spec.>

## Changelog

| Version | Date       | Change            |
|---------|------------|-------------------|
| 1       | YYYY-MM-DD | Initial version   |
```

- [ ] **Step 2: Write `templates/adr.md`**

```markdown
---
id: ADR-XXXX
title: <Short decision title>
status: proposed      # proposed | accepted | superseded | deprecated | rejected
date: YYYY-MM-DD
supersedes: null      # ADR id this decision replaces, if any
superseded_by: null   # filled when a later ADR replaces this one
---

# ADR-XXXX - <Short decision title>

## Context

<What situation forced a decision. If this supersedes an ADR: what changed
since that decision - this is the only legitimate home for "it was A, now B".>

## Decision

<"We will ..." - one clear statement.>

## Consequences

<What becomes easier, what becomes harder, required migrations. If this
supersedes ADR-YYYY: state that ADR-YYYY was marked superseded and which spec
was updated to reflect the new decision.>
```

- [ ] **Step 3: Commit**

```bash
git add templates/
git commit -m "feat: add spec and ADR templates

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: Skill sdd-source-of-truth

**Files:**
- Create: `skills/sdd-source-of-truth/SKILL.md`

**Interfaces:**
- Consumes: `templates/spec.md`, `templates/adr.md` (Task 3).
- Produces: skill name `sdd-source-of-truth` — referenced by Tasks 5, 6, 7.

- [ ] **Step 1: Write `skills/sdd-source-of-truth/SKILL.md` — full content**

```markdown
---
name: sdd-source-of-truth
description: Use when reading or editing anything under docs/specs/, docs/decisions/, or docs/_archive/, or when determining what the system's current behavior should be, in a project using the SDD convention (has docs/specs/). Defines the 3-layer model, authority order, frontmatter schemas, and the four lifecycle rules.
---

# SDD Source of Truth

Projects using this convention separate durable documentation into three
layers by mutability. Mixing layers in one file is what causes stale-doc
confusion, so never do it.

| Layer        | Question it answers      | Mutability                      | Location          |
|--------------|--------------------------|---------------------------------|-------------------|
| **Working**  | How are we doing it now? | Ephemeral - disposable on merge | `docs/plans/`     |
| **Spec**     | What must hold today?    | Living - edited in place        | `docs/specs/`     |
| **Decision** | Why did A become B?      | Immutable - append-only         | `docs/decisions/` |

## Authority order

When sources conflict, trust in this order:

1. `docs/specs/*` with `status: active` - what the system MUST do today
2. The code - what it actually does today
3. `docs/decisions/*` (ADRs) - WHY it changed from A to B
4. `docs/_archive/*` - history only. Ignore by default.

If an active spec and the code diverge, the spec wins: align the code and
record the reconciliation in an ADR. Never silently edit a spec to match
drifted code.

## Frontmatter schemas

Spec (`docs/specs/NNN-domain.md`):

    ---
    id: SPEC-001
    title: Payments module
    status: active        # draft | active | superseded | archived
    version: 3            # bump on every behavior change
    updated: 2026-07-19
    owner: payments-team
    supersedes: []
    superseded_by: null
    canonical: true       # agents only trust canonical: true + status: active
    ---

ADR (`docs/decisions/NNNN-title.md`):

    ---
    id: ADR-0002
    title: Switch persistence to DynamoDB
    status: accepted      # proposed | accepted | superseded | deprecated | rejected
    date: 2026-07-19
    supersedes: ADR-0001  # or null
    superseded_by: null
    ---

Full body templates: `${CLAUDE_PLUGIN_ROOT}/templates/spec.md` and
`${CLAUDE_PLUGIN_ROOT}/templates/adr.md`.

## The four lifecycle rules

1. **Specs are living documents.** Edit in place, bump `version` and
   `updated`. NEVER create `payments-v2.md` next to `payments.md`.
2. **Contradiction requires an ADR.** A behavior change that contradicts a
   previous decision gets a new ADR with `supersedes:` pointing at the old
   one; the old one gets `status: superseded` and `superseded_by` filled. The
   ADR is the ONLY place a contradiction may legitimately exist.
3. **Retire, never delete.** Retired spec: `status: archived`,
   `superseded_by` filled, file moved to `docs/_archive/`. ADRs are never
   deleted.
4. **Plans are disposable.** On merge, promote what survives (to a spec or an
   ADR) and move the plan to `docs/plans/archive/`. Never infer current state
   from a plan.

## Hygiene

- Keep the index table in `docs/specs/README.md` in sync (id, domain, status,
  version, updated) and the decision log in `docs/decisions/README.md`.
- A spec never narrates history ("previously X"). Present tense only; the
  "before" lives in ADRs.
- If `scripts/check-docs.py` exists in the project, run
  `python scripts/check-docs.py docs` after any docs change and fix
  violations.
- Write project docs in the project's language (match existing docs; ask if
  unclear). Frontmatter keys and status values stay in English - the linter
  depends on them.
```

- [ ] **Step 2: Sanity-check the frontmatter description length**

Run (PowerShell): `$m = Get-Content skills/sdd-source-of-truth/SKILL.md -Raw; ([regex]::Match($m, '(?s)description: (.+?)\n---').Groups[1].Value.Length)`
Expected: a number below 1024.

- [ ] **Step 3: Commit**

```bash
git add skills/sdd-source-of-truth/
git commit -m "feat: add sdd-source-of-truth skill

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: Skill sdd-finalize

**Files:**
- Create: `skills/sdd-finalize/SKILL.md`

**Interfaces:**
- Consumes: skill name `sdd-source-of-truth` (Task 4), templates (Task 3).
- Produces: skill directory name `sdd-finalize` — MUST match the name used in the hook's block reason (Task 2).

- [ ] **Step 1: Write `skills/sdd-finalize/SKILL.md` — full content**

```markdown
---
name: sdd-finalize
description: Use when finishing a feature, plan, branch, or any task that changed code in a project using the SDD convention (has docs/specs/) - promotes durable knowledge into specs/ADRs so documentation stays the single source of truth. Also invoke when the SDD Stop hook reports that code changed without a docs update.
---

# SDD Finalize

Every task that changed behavior must end by updating the durable
documentation layer. Run this checklist top to bottom. If you have not read
the sdd-source-of-truth skill this session, read it first.

## Checklist

1. **List what changed.** Which behavior is new or altered? Which
   architectural decisions were made? Use your own edits this session and
   `git diff` if available.
2. **Behavior changed?** Edit the canonical spec in `docs/specs/` **in
   place**: describe the present only, bump `version`, set `updated` to
   today. If no spec covers this domain yet, create one from
   `${CLAUDE_PLUGIN_ROOT}/templates/spec.md` with the next SPEC id.
3. **Decision made, or a previous decision contradicted?** Create a new ADR
   from `${CLAUDE_PLUGIN_ROOT}/templates/adr.md` with the next ADR id. If it
   contradicts an earlier ADR: set `supersedes:` on the new one, and on the
   old one set `status: superseded` plus `superseded_by`.
4. **Plan finished?** Move it from `docs/plans/active/` to
   `docs/plans/archive/`. Anything durable in it must have been promoted in
   steps 2-3 first.
5. **Update the indexes:** the table in `docs/specs/README.md` and the
   decision log in `docs/decisions/README.md`.
6. **Run the linter** if the project has it:
   `python scripts/check-docs.py docs`. Fix violations before finishing.
7. **Nothing durable changed?** (pure refactor, typo, formatting, tooling,
   dependency bump with no behavior change) - say so explicitly to the user
   in one sentence, e.g. "No spec/ADR update needed: pure refactor, no
   behavior change." That statement is the legitimate exit from the Stop
   hook reminder. Never fabricate a doc update to silence it.

## Rules that trip agents up

- Never narrate history in a spec ("previously X"). Present tense only;
  history lives in ADRs.
- One canonical spec per domain. Consolidate; never fork a v2 file.
- Docs follow the project's language, not English by default. Frontmatter
  keys and status values stay in English.
- Updating a plan checkbox is NOT a docs update. Only `docs/specs/` and
  `docs/decisions/` count as durable.
```

- [ ] **Step 2: Cross-check the hook reason string**

Run: `python -c "import re,pathlib; t=pathlib.Path('hooks/check-docs-updated.py').read_text(); assert 'sdd-finalize' in t; print('ok')"`
Expected: `ok` (the hook's reason names this skill exactly).

- [ ] **Step 3: Commit**

```bash
git add skills/sdd-finalize/
git commit -m "feat: add sdd-finalize skill

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: Skill sdd-retrofit

**Files:**
- Create: `skills/sdd-retrofit/SKILL.md`

**Interfaces:**
- Consumes: skill names `sdd-source-of-truth` (Task 4); templates (Task 3); the `/sdd-init` behavior contract (Task 7 mirrors it — scaffold copy + CLAUDE.md merge).
- Produces: skill name `sdd-retrofit` — referenced by the `/sdd-retrofit` command (Task 7).

- [ ] **Step 1: Write `skills/sdd-retrofit/SKILL.md` — full content**

```markdown
---
name: sdd-retrofit
description: Use only when the user runs /sdd-retrofit - interactive playbook to migrate an existing, messy documentation base into the SDD convention through inventory, per-domain triage with user approval, consolidation into living specs, ADRs for contradictions, and archiving.
---

# SDD Retrofit

Interactive migration of an existing project's documentation into the SDD
convention. Read the sdd-source-of-truth skill first. Never bulk-rewrite
without approval: triage is judgment, and a wrong call becomes a wrong source
of truth.

## Phase 1 - Inventory (no deep reading)

1. List doc artifacts with paths and dates only: directory listing of doc
   folders plus, when git is available,
   `git log --format="%ad" --date=short -1 -- <path>` per file. Do NOT load
   full contents into context.
2. Read at most the first ~20 lines of each file - just enough to classify
   its domain and kind.
3. Show the user an inventory table: path, apparent domain, last modified,
   kind (spec-like / plan-like / decision-like / other).

## Phase 2 - Domain map (approval gate)

Propose a domain map: which files belong to which domain, and which single
file (or merge of files) should become the canonical spec of each domain.
Ask the user to approve or correct the map before touching anything. Also ask
which domain confuses agents the most - start there. No big bang: one domain
at a time.

## Phase 3 - Per-domain triage (approval gate per domain)

For the current domain, propose sorting every artifact into 3 buckets:

- **Canonical** - describes today's truth (or its newest version). Becomes or
  merges into the living spec.
- **Historical** - a past decision worth keeping. Distilled into an ADR.
- **Dead** - obsolete, no remaining value. Archived as-is.

Show the buckets and wait for the user's approval of this domain. Then
execute:

1. Consolidate the canonical bucket into ONE living spec at
   `docs/specs/NNN-<domain>.md` using
   `${CLAUDE_PLUGIN_ROOT}/templates/spec.md`. Present tense only - strip any
   "previously X" narration you find while merging.
2. Every "A became B" contradiction found becomes a short ADR from
   `${CLAUDE_PLUGIN_ROOT}/templates/adr.md`, capturing what changed and why.
   Chain `supersedes`/`superseded_by` when one decision replaced another.
3. Move historical and dead originals to `docs/_archive/` with
   `status: archived` and `superseded_by` pointing at the new spec or ADR.
   Prefix archived filenames with the retirement date (YYYY-MM-). Never
   delete.
4. Update the index in `docs/specs/README.md` and the log in
   `docs/decisions/README.md`.

Repeat Phase 3 for the next approved domain.

## Phase 4 - Setup

Finish exactly like /sdd-init: copy any missing scaffold pieces (index
READMEs, `docs/plans/active|archive/`, `docs/_archive/`,
`scripts/check-docs.py`), merge the CLAUDE.md rules block, ask about the
project docs language, and offer wiring `check-docs.py` into CI. Then run
`python scripts/check-docs.py docs` and show the result.
```

- [ ] **Step 2: Commit**

```bash
git add skills/sdd-retrofit/
git commit -m "feat: add sdd-retrofit skill

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: Commands

**Files:**
- Create: `commands/sdd-init.md`
- Create: `commands/sdd-retrofit.md`

**Interfaces:**
- Consumes: scaffold file layout (Task 8 must ship exactly the files listed here), skill names `sdd-source-of-truth` and `sdd-retrofit`, marker strings `<!-- sdd-convention:start -->` / `<!-- sdd-convention:end -->` (Task 8's scaffold/CLAUDE.md must contain them).
- Produces: commands installed as `/sdd-convention:sdd-init` and `/sdd-convention:sdd-retrofit` (short forms `/sdd-init`, `/sdd-retrofit`).

- [ ] **Step 1: Write `commands/sdd-init.md` — full content**

```markdown
---
description: Set up the SDD convention in this project (docs structure, CLAUDE.md rules block, hygiene linter)
argument-hint: [docs language, e.g. "en" or "pt-BR"]
---

Set up the SDD documentation convention in the current project. Read the
sdd-source-of-truth skill first if you have not this session. Every step is
idempotent: when a piece already exists, leave it untouched and report it.

The plugin's assets live at ${CLAUDE_PLUGIN_ROOT} (scaffold/ and templates/).
If that variable did not expand, locate the sdd-convention plugin directory
under ~/.claude/plugins/.

1. Docs language: use $ARGUMENTS if given; otherwise detect from existing
   project docs; otherwise ask the user.
2. Copy from ${CLAUDE_PLUGIN_ROOT}/scaffold/ into the project whichever of
   these do not exist yet:
   - docs/specs/README.md            (spec index)
   - docs/decisions/README.md        (decision log)
   - docs/plans/README.md, docs/plans/active/.gitkeep, docs/plans/archive/.gitkeep
   - docs/_archive/README.md
   - scripts/check-docs.py
   Do NOT copy the example spec/ADR/archive files (001-example-feature.md,
   0001/0002-*.md, 2026-01-example-payments-v1.md) into real projects.
3. CLAUDE.md rules block:
   - No CLAUDE.md in the project: copy ${CLAUDE_PLUGIN_ROOT}/scaffold/CLAUDE.md.
   - CLAUDE.md exists without the markers: append the section between
     <!-- sdd-convention:start --> and <!-- sdd-convention:end --> (inclusive)
     from the scaffold file.
   - Markers already present: replace the content between them with the
     scaffold's current version (this is how plugin upgrades propagate).
   - If the project uses AGENTS.md instead of CLAUDE.md, apply the same logic
     to AGENTS.md.
4. If the chosen docs language is not English, translate the copied index
   READMEs and the CLAUDE.md block body into it. Keep frontmatter keys and
   status values in English - the linter depends on them.
5. Run `python scripts/check-docs.py docs` and show the output.
6. Report: what was created, what already existed, and suggest adding
   `python scripts/check-docs.py docs` to CI.
```

- [ ] **Step 2: Write `commands/sdd-retrofit.md` — full content**

```markdown
---
description: Interactively migrate an existing messy documentation base into the SDD convention
argument-hint: [optional: directories or domains to scope the retrofit]
---

Invoke the sdd-retrofit skill and follow it exactly - interactive, with user
approval gates per phase. If arguments were given, scope the retrofit to
them: $ARGUMENTS
```

- [ ] **Step 3: Commit**

```bash
git add commands/
git commit -m "feat: add /sdd-init and /sdd-retrofit commands

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 8: Scaffold in English

**Files:**
- Modify: `scaffold/CLAUDE.md` (rewrite in English, add markers)
- Modify: `scaffold/docs/specs/README.md`, `scaffold/docs/specs/001-example-feature.md`
- Modify: `scaffold/docs/decisions/README.md`, `scaffold/docs/decisions/0001-example-decision.md`, `scaffold/docs/decisions/0002-supersede-example.md`
- Modify: `scaffold/docs/plans/README.md`
- Modify: `scaffold/docs/_archive/README.md`, `scaffold/docs/_archive/2026-01-example-payments-v1.md`
- Modify: `scaffold/scripts/check-docs.py` (English docstring/messages only — logic unchanged)
- Create: `scaffold/docs/plans/active/.gitkeep`, `scaffold/docs/plans/archive/.gitkeep`

**Interfaces:**
- Consumes: marker strings from Task 7's command contract.
- Produces: `scaffold/CLAUDE.md` containing `<!-- sdd-convention:start -->` and `<!-- sdd-convention:end -->`; scaffold passing `check-docs.py`.

- [ ] **Step 1: Rewrite `scaffold/CLAUDE.md` — full content**

```markdown
# Project memory - READ THIS FIRST

<!-- sdd-convention:start -->
> This section is managed by the sdd-convention plugin. It tells any agent
> **where the truth lives** and **how to tell what is current**. Do not repeat
> spec content here; point to it.

## Single source of truth

The **only** canonical specs live in `docs/specs/` with `status: active` in
the frontmatter. If a document sits in `docs/_archive/` or carries
`status: superseded`/`archived`, do **NOT** treat it as current - it is
history.

Authority order when sources conflict:

1. `docs/specs/*` with `status: active`  - what the system MUST do today
2. The code  - what it actually does today
3. `docs/decisions/*` (ADRs)  - WHY it changed from A to B
4. `docs/_archive/*`  - the past, archaeology only. Ignore by default.

If an active spec and the code diverge, the spec wins: align the code and
record the reconciliation in an ADR. Never "fix" the divergence by silently
editing the old spec.

## How to find what is current (without reading everything)

- `docs/specs/README.md`     - index of active specs + status
- `docs/decisions/README.md` - decision log (the "from A to B and why")
- `docs/plans/`              - work in progress. Ephemeral.

## Rules for agents editing documentation

1. **Specs are living documents.** Edit the spec in place and bump
   `version`/`updated`. NEVER create `payments-v2.md` next to `payments.md`.
2. **Any behavior change that contradicts a previous decision requires a new
   ADR** in `docs/decisions/` with `supersedes: ADR-XXXX`. The ADR is the
   only place where the contradiction may live.
3. **Never delete an ADR.** Mark it `status: superseded` and write the new
   one.
4. **Retire specs, never delete.** When retiring a spec: `status: archived`,
   fill `superseded_by`, move the file to `docs/_archive/`.
5. **Plans** live in `docs/plans/active/` while open and move to
   `docs/plans/archive/` when merged. Anything durable graduates to a spec or
   an ADR - the plan itself is disposable.

## Finishing work

At the end of any task that changed behavior, promote what survives:

- New or changed behavior - update the canonical **spec** in `docs/specs/`.
- Architecture choice / trade-off - write an **ADR** in `docs/decisions/`.
- The plan goes to `docs/plans/archive/`. It is not a source of truth.
<!-- sdd-convention:end -->
```

- [ ] **Step 2: Rewrite `scaffold/docs/specs/README.md` — full content**

````markdown
# Specs (the living source of truth)

Each file here describes **what the system must do today** for one domain.
These are **living** documents: edited in place, versioned via frontmatter,
one per domain. There is no "v2 next to v1" - there is the spec, plus its
history in git and in the ADRs.

## Active spec index

| ID       | Domain              | Status | Version | Updated    |
|----------|---------------------|--------|---------|------------|
| SPEC-001 | Example module      | active | 3       | 2026-07-19 |

> Keep this table as the index readable by humans and agents. An `archived`
> spec leaves this table and moves to `docs/_archive/`.

## Required frontmatter

```yaml
---
id: SPEC-001
title: Payments module
status: active        # draft | active | superseded | archived
version: 3            # bump on every behavior change
updated: 2026-07-19
owner: payments-team
supersedes: []        # spec ids this one consolidated
superseded_by: null   # filled when it becomes archived
canonical: true       # agents only trust canonical: true + status: active
---
```
````

- [ ] **Step 3: Rewrite `scaffold/docs/specs/001-example-feature.md` — full content**

```markdown
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
```

- [ ] **Step 4: Rewrite `scaffold/docs/decisions/README.md` — full content**

````markdown
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

| ADR      | Title                             | Status     | Supersedes | Date       |
|----------|-----------------------------------|------------|------------|------------|
| ADR-0001 | Postgres as initial storage       | superseded | -          | 2026-01-10 |
| ADR-0002 | Switch persistence to DynamoDB    | accepted   | ADR-0001   | 2026-07-19 |

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
````

- [ ] **Step 5: Rewrite `scaffold/docs/decisions/0001-example-decision.md` — full content**

```markdown
---
id: ADR-0001
title: Postgres as initial storage
status: superseded
date: 2026-01-10
supersedes: null
superseded_by: ADR-0002
---

# ADR-0001 - Postgres as initial storage

> STATUS: **superseded by ADR-0002**. Kept for history. Not current.

## Context

At the start of the project we needed simple relational storage with strong
transactions and team familiarity.

## Decision

Use PostgreSQL as the primary database for the payments module.

## Consequences

- ACID transactions out of the box.
- Coupling to the relational model (high horizontal-scaling cost - which is
  what motivated ADR-0002).
```

- [ ] **Step 6: Rewrite `scaffold/docs/decisions/0002-supersede-example.md` — full content**

```markdown
---
id: ADR-0002
title: Switch persistence to DynamoDB
status: accepted
date: 2026-07-19
supersedes: ADR-0001
superseded_by: null
---

# ADR-0002 - Switch persistence to DynamoDB

## Context

Write volume grew and Postgres horizontal scaling became an operational
bottleneck. This is exactly the "it was A, now it is B" case: ADR-0001 said
Postgres; this decision supersedes it.

## Decision

Migrate the payments module's persistence to DynamoDB.

## Consequences

- Horizontal scale and predictable latency.
- Loses native multi-item transactions - idempotency handled in the
  application.
- **Required action:** SPEC-001 was updated (v3) to reflect DynamoDB, and
  ADR-0001 was marked `superseded`.

## Related

- Supersedes: ADR-0001
- Reflected in: SPEC-001 (v3)
```

- [ ] **Step 7: Rewrite `scaffold/docs/plans/README.md` — full content**

````markdown
# Plans (the working layer - ephemeral)

Work-in-progress artifacts live here (brainstorm - worktree - plan -
implement flows such as Superpowers). They are disposable by design: they
serve while the feature is open.

```
plans/
|- active/     # plans for in-flight features (1 per worktree/branch)
|- archive/    # plans of merged features - kept only for the paper trail
```

## Lifecycle rule

1. When a feature starts, its plan is born in `active/`
   (e.g. `active/2026-07-payments-dynamo.md`).
2. While working, the plan's checkboxes track progress.
3. On merge: **promote what is durable**, then move the plan to `archive/`.
   - New behavior - update the spec in `docs/specs/`.
   - Architecture trade-off - write an ADR in `docs/decisions/`.
4. A plan in `archive/` is **not** a source of truth. Agents must not infer
   current state from it.

> Why separate from specs/decisions: a plan is *how we are doing it now*; a
> spec is *what must hold*; an ADR is *why we decided so*. Three different
> mutabilities - never mix them in one file.
````

- [ ] **Step 8: Rewrite `scaffold/docs/_archive/README.md` — full content**

```markdown
# _archive (history - invisible to agents by default)

Retired specs live here. A document in this directory is **never** current.
It exists for human archaeology; agents must ignore it when reasoning about
the system's state (the CLAUDE.md rules block says so explicitly).

Rules:

- Every file here has `status: archived` and `superseded_by` filled.
- Do not delete (git remembers anyway, but the header makes the intent
  explicit and readable without `git log`).
- Prefix with the retirement date for ordering:
  `2026-01-example-payments-v1.md`.
```

- [ ] **Step 9: Rewrite `scaffold/docs/_archive/2026-01-example-payments-v1.md` — full content**

```markdown
---
id: SPEC-001
title: Payments module (v1 - archived)
status: archived
version: 1
updated: 2026-01-10
archived: 2026-07-19
supersedes: []
superseded_by: SPEC-001@active
canonical: false
---

# [ARCHIVED] Payments module - v1

> This is a historical version preserved as an example of what happens when a
> spec is retired. **It is not current.** The live version is
> `docs/specs/001-example-feature.md`. Kept only to trace how the behavior
> looked before ADR-0002.

## Behavior (historical)

- Persistence: Postgres (see ADR-0001, superseded).
- No charge idempotency (added in v2).
```

- [ ] **Step 10: Translate `scaffold/scripts/check-docs.py` strings to English — logic unchanged**

Replace the module docstring and user-facing strings; keep every check as-is:

```python
#!/usr/bin/env python3
"""check-docs.py - validates SDD artifact hygiene.

No external dependencies: parses the "flat" YAML frontmatter (key: value and
simple [a, b] lists) of specs (docs/specs, docs/_archive) and ADRs
(docs/decisions).

Fails (exit 1) on any of these violations:
  1. Two specs with `status: active` sharing the same `id`.
  2. A `superseded`/`archived` doc without `superseded_by`.
  3. An ADR with `supersedes: X` where X does not exist or is not `superseded`.
  4. Duplicate `id` among ADRs.
  5. Missing frontmatter or missing `id`/`status`.

Usage:  python scripts/check-docs.py [docs_root]   (default: ./docs)
"""
import sys
import re
from pathlib import Path

def parse_frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    body = text[3:end].strip("\n")
    data = {}
    for line in body.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if not m:
            continue
        key, raw = m.group(1), m.group(2).strip()
        if raw in ("null", "~", ""):
            val = None
        elif raw.startswith("[") and raw.endswith("]"):
            inner = raw[1:-1].strip()
            val = [x.strip() for x in inner.split(",") if x.strip()] if inner else []
        else:
            val = raw.strip().strip('"').strip("'")
        data[key] = val
    return data

def load(root):
    docs = []
    for p in sorted(Path(root).rglob("*.md")):
        if p.name.upper() == "README.MD":
            continue
        fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        if fm is not None:
            docs.append((p, fm))
    return docs

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs")
    if not root.exists():
        print(f"[error] folder not found: {root}")
        return 1

    docs = load(root)
    errors, warnings = [], []

    # minimum frontmatter
    for p, fm in docs:
        for req in ("id", "status"):
            if req not in fm:
                errors.append(f"{p}: frontmatter missing '{req}'")

    specs = [(p, fm) for p, fm in docs if str(fm.get("id", "")).startswith("SPEC")]
    adrs = [(p, fm) for p, fm in docs if str(fm.get("id", "")).startswith("ADR")]

    # 1. two active specs with the same id
    active_ids = {}
    for p, fm in specs:
        if fm.get("status") == "active":
            active_ids.setdefault(fm.get("id"), []).append(p)
    for sid, paths in active_ids.items():
        if len(paths) > 1:
            errors.append(f"SPEC id '{sid}' has >1 active doc: {[str(x) for x in paths]}")

    # 2. superseded/archived without superseded_by
    for p, fm in docs:
        if fm.get("status") in ("superseded", "archived") and not fm.get("superseded_by"):
            errors.append(f"{p}: status '{fm.get('status')}' but no 'superseded_by'")

    # 3/4. ADR integrity
    adr_by_id = {}
    for p, fm in adrs:
        aid = fm.get("id")
        if aid in adr_by_id:
            errors.append(f"duplicate ADR id: {aid} in {p} and {adr_by_id[aid][0]}")
        adr_by_id[aid] = (p, fm)
    for p, fm in adrs:
        sup = fm.get("supersedes")
        targets = sup if isinstance(sup, list) else ([sup] if sup else [])
        for t in targets:
            if t not in adr_by_id:
                errors.append(f"{p}: supersedes '{t}' which does not exist")
            elif adr_by_id[t][1].get("status") != "superseded":
                warnings.append(
                    f"{p}: supersedes '{t}', but '{t}' is not marked 'superseded' "
                    f"(it is '{adr_by_id[t][1].get('status')}')"
                )

    print(f"Checked {len(docs)} docs ({len(specs)} specs, {len(adrs)} ADRs).")
    for w in warnings:
        print(f"  [warn] {w}")
    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  [ERROR] {e}")
        return 1
    print("OK - no hygiene violations found.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 11: Create the plans subdirectory keepers**

Create empty files `scaffold/docs/plans/active/.gitkeep` and `scaffold/docs/plans/archive/.gitkeep`.

- [ ] **Step 12: Verify the scaffold passes its own linter and carries the markers**

Run: `python scaffold/scripts/check-docs.py scaffold/docs`
Expected: `Checked 4 docs (2 specs, 2 ADRs).` then `OK - no hygiene violations found.` and exit 0.

Run: `python -c "import pathlib; t = pathlib.Path('scaffold/CLAUDE.md').read_text(encoding='utf-8'); assert '<!-- sdd-convention:start -->' in t and '<!-- sdd-convention:end -->' in t; print('markers ok')"`
Expected: `markers ok`.

- [ ] **Step 13: Commit**

```bash
git add scaffold/
git commit -m "feat: rewrite scaffold in English with CLAUDE.md merge markers

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 9: README in English

**Files:**
- Modify: `README.md` (full rewrite)

**Interfaces:**
- Consumes: install names from Task 1 (`sdd-convention@sdd-convention`), command names from Task 7, skill names from Tasks 4-6, marker contract from Task 8.

- [ ] **Step 1: Rewrite `README.md` — full content**

````markdown
# sdd-convention

**Spec-driven development with a single source of truth - as an installable
Claude Code plugin.**

Old specs that say "A" fight new ones that say "actually, B" and quietly
degrade your agent's reasoning. The bottleneck is not artifact volume - it is
the lack of a single source of truth and of obsolescence marking. Embeddings
will not save you: similarity search happily returns the chunk saying "A" and
the chunk saying "B" in the same answer. The fix is **lifecycle governance**,
not retrieval.

This plugin makes an agent:

1. **Know where the truth lives** - a 3-layer convention (living specs,
   append-only decision records, disposable plans) with machine-readable
   frontmatter.
2. **Close the loop** - a Stop hook notices when a turn changed code without
   updating specs/ADRs and makes the agent either update them or explicitly
   state that nothing durable changed.
3. **Migrate existing messes** - an interactive retrofit playbook (inventory,
   per-domain triage with your approval, consolidation, archive).

## Install (Claude Code)

```
/plugin marketplace add pablopupulin/sdd-convention
/plugin install sdd-convention@sdd-convention
```

Then, in each project that should use the convention:

- New/clean project: run `/sdd-init`
- Existing messy docs: run `/sdd-retrofit`

The Stop hook only acts in projects that have a `docs/specs/` directory -
installing the plugin globally does not affect other projects.

## What you get

| Piece | What it does |
|---|---|
| Skill `sdd-source-of-truth` | The convention: 3 layers, authority order, frontmatter schemas, lifecycle rules. Loads when the agent touches durable docs. |
| Skill `sdd-finalize` | The closing checklist: promote changes into specs/ADRs, archive plans, update indexes. Loads when finishing work - and when the hook fires. |
| Skill `sdd-retrofit` | Interactive migration playbook for existing doc bases. |
| `/sdd-init` | Scaffolds `docs/`, merges a managed rules block into CLAUDE.md, installs the hygiene linter. |
| `/sdd-retrofit` | Runs the retrofit playbook. |
| Stop hook | Fail-open reminder: code changed but no spec/ADR touched - finalize before stopping. |
| `scripts/check-docs.py` | CI linter: duplicate active specs, archived docs without `superseded_by`, broken ADR supersede chains. |

## The convention in 60 seconds

Almost every SDD artifact is one of three things, each with its own mutation
policy. Mixing them in one file is what creates confusion.

| Layer        | Question it answers      | Mutability                      | Lives in          |
|--------------|--------------------------|---------------------------------|-------------------|
| **Working**  | How are we doing it now? | Ephemeral - disposable on merge | `docs/plans/`     |
| **Spec**     | What must hold today?    | Living - edited in place        | `docs/specs/`     |
| **Decision** | Why did A become B?      | Immutable - append-only         | `docs/decisions/` |

Golden rule: a **spec** never narrates history ("it used to be X"). It
describes only the present. The history ("it was X, we changed it because Y")
lives in an **ADR**. And a **plan** is garbage after the merge - whatever
survives graduates into a spec or an ADR.

Authority order when sources conflict:

1. `docs/specs/*` with `status: active` - what the system MUST do today
2. The code - what it actually does today
3. `docs/decisions/*` (ADRs) - WHY it changed from A to B
4. `docs/_archive/*` - history. Ignored by default.

Every durable doc carries machine-readable frontmatter (see
`templates/spec.md` and `templates/adr.md`), which is what lets an agent - and
the linter - know what is canonical without reading everything:

```yaml
---
id: SPEC-001
status: active        # draft | active | superseded | archived
version: 3
updated: 2026-07-19
superseded_by: null
canonical: true       # agents only trust canonical: true + status: active
---
```

Four lifecycle rules make it work:

1. **Specs are living.** Edit in place, bump `version`/`updated`. Never
   create `payments-v2.md` next to `payments.md`.
2. **Contradiction requires an ADR.** New ADR with `supersedes:`, old one
   marked `superseded`. The ADR is the only place a contradiction may exist.
3. **Retire, never delete.** `status: archived` + `superseded_by` + move to
   `docs/_archive/`.
4. **Plans are disposable.** Promote the durable part on merge, archive the
   plan.

## Project layout after /sdd-init

```
your-repo/
|- CLAUDE.md                     # agent entry point: managed rules block
|- docs/
|  |- specs/                     # CANONICAL and living - edited in place
|  |  |- README.md               #   index + status of all active specs
|  |- decisions/                 # ADRs - append-only, the "why A became B"
|  |  |- README.md
|  |- plans/                     # working layer - ephemeral
|  |  |- active/
|  |  |- archive/
|  |- _archive/                  # retired specs - invisible to agents
|- scripts/
   |- check-docs.py              # hygiene linter (run it in CI)
```

## Using it with other agents (Codex, Cursor, ...)

The skills follow the open [Agent Skills](https://agentskills.io) format
(`SKILL.md` with `name`/`description` frontmatter):

1. Copy the `skills/` directories into your agent's skills location.
2. Add the rules block to your `AGENTS.md` (same content as
   `scaffold/CLAUDE.md` between the `sdd-convention` markers), plus this
   enforcement line - other agents do not run the Stop hook, so the closing
   step must be instructed:

```markdown
## Finishing work (SDD convention)

Before ending any task that changed code: update the canonical spec in
docs/specs/ (bump version/updated) and/or write an ADR in docs/decisions/
for any decision or contradiction - or state explicitly that nothing durable
changed. Never narrate history inside a spec; history lives in ADRs. Then run
`python scripts/check-docs.py docs` if present.
```

## Where RAG/Obsidian fits

Not as the source of truth - as a **search index over the canonical set**,
once it grows too big to scan. Only index `status: active` +
`canonical: true`. Never vectorize `docs/_archive/`. Retrieval can no longer
resurrect the old "A", because the old "A" is simply not in the index.

## Prior art

This packages battle-tested pieces rather than inventing new ones:

- [ADR / MADR](https://adr.github.io/madr/) - decision records; the
  `superseded` status exists precisely for "A became B".
- [GitHub Spec Kit](https://github.com/github/spec-kit) - SDD scaffolding
  (`constitution.md` maps to the CLAUDE.md rules block).
- [AGENTS.md](https://agents.md) - cross-tool agent memory file.
- [Superpowers](https://github.com/obra/superpowers) - the working layer
  (brainstorm - plan - implement); this convention adds the durable layer on
  top, without fighting it.

None of them is a vectorizer that resolves contradictions - they all attack
the problem through governance and state, which is the right side.

## Development

```
python -m pytest tests/ -v                        # hook tests
python scaffold/scripts/check-docs.py scaffold/docs  # linter self-check
claude plugin validate .                          # manifest validation
```

## License

MIT
````

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README in English as plugin documentation

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 10: CI and full local validation

**Files:**
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: `tests/` (Task 2), `scaffold/` (Task 8), manifests (Task 1).

- [ ] **Step 1: Write `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install test dependencies
        run: python -m pip install pytest
      - name: Hook tests
        run: python -m pytest tests/ -v
      - name: Scaffold hygiene linter self-check
        run: python scaffold/scripts/check-docs.py scaffold/docs
      - name: Validate manifests are JSON
        run: |
          python -m json.tool .claude-plugin/plugin.json
          python -m json.tool .claude-plugin/marketplace.json
          python -m json.tool hooks/hooks.json
```

- [ ] **Step 2: Run everything locally**

Run: `python -m pytest tests/ -v && python scaffold/scripts/check-docs.py scaffold/docs`
Expected: all tests PASS; linter prints `OK - no hygiene violations found.`

- [ ] **Step 3: Validate the plugin with the official CLI**

Run: `claude plugin validate .`
Expected: validation passes for both plugin.json and marketplace.json (warnings acceptable, errors are not). If the `claude` CLI subcommand is unavailable in this environment, note it and rely on the JSON checks + Step 4.

- [ ] **Step 4: Install locally end-to-end**

Run: `claude plugin marketplace add e:/Pupulin/sdd-convention && claude plugin install sdd-convention@sdd-convention --scope user`
Expected: install succeeds. Then verify the pieces landed: the marketplace lists the plugin (`claude plugin marketplace list`).
Cleanup (optional, keep installed if the user wants to dogfood): `claude plugin marketplace list` to confirm state and report to the user.

- [ ] **Step 5: Commit**

```bash
git add .github/
git commit -m "ci: add GitHub Actions workflow (hook tests, linter, manifest checks)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 11: Publish to GitHub

**Files:**
- None created — repo operations only.

**Interfaces:**
- Consumes: everything committed in Tasks 1-10; repo name `pablopupulin/sdd-convention` (public), tag `v0.1.0`.

- [ ] **Step 1: Preflight**

Run: `git status --porcelain` (expect empty) and `gh auth status`
Expected: clean tree; gh authenticated as pablopupulin. If gh is missing or unauthenticated, STOP and ask the user to run `gh auth login` — do not improvise credentials.

- [ ] **Step 2: Create the public repo and push**

```bash
gh repo create pablopupulin/sdd-convention --public --source . --push \
  --description "Spec-driven development with a single source of truth - installable Claude Code plugin (skills + commands + Stop hook)"
```

Expected: repo created, `main` pushed, `origin` remote configured.

- [ ] **Step 3: Tag the release**

```bash
git tag v0.1.0
git push origin v0.1.0
```

- [ ] **Step 4: Verify the published install path**

Run: `claude plugin marketplace add pablopupulin/sdd-convention`
Expected: succeeds (this proves the GitHub shorthand resolves). If the local-path marketplace from Task 10 conflicts, remove it first (`claude plugin marketplace remove sdd-convention`) and re-add from GitHub.

- [ ] **Step 5: Report to the user**

Tell the user: repo URL, the two install commands (`/plugin marketplace add pablopupulin/sdd-convention`, `/plugin install sdd-convention@sdd-convention`), and that CI runs on push. Suggest an end-to-end smoke test in a real project: install, run `/sdd-init` in a scratch project, make a code edit, watch the Stop hook fire.
