# Ecosystem Adapters (OpenSpec Support) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the sdd-convention plugin work in OpenSpec projects (and be one-dict-entry extensible to Spec Kit etc.): descriptive ecosystem adapters in the Stop hook, `.sdd.json` override, hybrid `/sdd-init`, ecosystem-aware skills, release v0.2.0.

**Architecture:** Each ecosystem is data (`{detect, durable, ignore}`) in an `ECOSYSTEMS` dict inside the hook — no adapter code. Detection unions every ecosystem whose detect dir exists; optional `.sdd.json` forces/extends. The Decision layer (ADRs) is always `docs/decisions/`. Native-mode behavior stays byte-identical to v0.1.x.

**Tech Stack:** Python 3 stdlib (hook), pytest (tests), Claude Code plugin assets (skills/commands/scaffold markdown).

**Design doc:** `docs/plans/active/2026-07-19-openspec-ecosystem-adapters-design.md`

## Global Constraints

- **Native-mode behavior byte-identical to v0.1.x**: the existing 18 tests in `tests/test_check_docs_updated.py` must pass UNMODIFIED. Only new tests are added (10 new → 28 total).
- Hook stays a single-file, **Python 3 stdlib only**, and keeps the **total fail-open** guarantee (`main()` wraps `_run()` in `except Exception: return 0`; always exit 0).
- `.sdd.json` keys: exactly `ecosystems`, `extra_durable`, `extra_ignore`. Malformed/missing file → pure auto-detection. `{"ecosystems": []}` disables the hook for the project.
- ADR home is ALWAYS `docs/decisions/`, in every ecosystem.
- Adapters table (exact values):
  - `native`: detect `docs/specs`, durable `docs/specs/` + `docs/decisions/`, ignore `docs/`
  - `openspec`: detect `openspec/specs`, durable `openspec/specs/` + `docs/decisions/`, ignore `openspec/` + `docs/`
- All plugin content in English. Skill frontmatter `description` under 1024 characters.
- Marker strings `<!-- sdd-convention:start -->` / `<!-- sdd-convention:end -->` unchanged; the new `scaffold/CLAUDE-openspec.md` must carry them too.
- Version: **0.2.0** in `.claude-plugin/plugin.json` AND `.claude-plugin/marketplace.json`; git tag `v0.2.0`.
- The hook's block `reason` must still contain the literal string `sdd-finalize` (tests assert it).
- Each task ends with a commit; commit messages end with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- This repo itself follows the SDD convention (see `CLAUDE.md`): Task 6 is the mandatory finalize (SPEC-001 bump + ADR-0005 + indexes + archive plans).

## File Structure (changes)

```
hooks/check-docs-updated.py        # Task 1: ECOSYSTEMS dict + .sdd.json + classification
tests/test_check_docs_updated.py   # Task 1: +1 helper, +10 tests (existing 18 untouched)
scaffold/CLAUDE-openspec.md        # Task 2: NEW - OpenSpec variant of the rules block
commands/sdd-init.md               # Task 3: hybrid (native/openspec) rewrite
skills/sdd-source-of-truth/SKILL.md# Task 4: Ecosystems section
skills/sdd-finalize/SKILL.md       # Task 4: OpenSpec branch in checklist
skills/sdd-retrofit/SKILL.md       # Task 4: Phase 0 ecosystem detection
README.md                          # Task 5: Ecosystem adapters section + hook line + prior art
.claude-plugin/plugin.json         # Task 5: version 0.2.0
.claude-plugin/marketplace.json    # Task 5: version 0.2.0
docs/specs/001-plugin-architecture.md  # Task 6: v2
docs/decisions/0005-*.md           # Task 6: NEW ADR
docs/specs/README.md, docs/decisions/README.md  # Task 6: indexes
docs/plans/active/* -> docs/plans/archive/      # Task 6: archive both working docs
```

---

### Task 1: Hook ecosystem adapters (TDD)

**Files:**
- Test: `tests/test_check_docs_updated.py` (append helper + 10 tests; DO NOT touch the existing 18 tests or helpers)
- Modify: `hooks/check-docs-updated.py` (full new content below)

**Interfaces:**
- Produces: `ECOSYSTEMS` dict with entries `native` and `openspec` (fields `detect`, `durable`, `ignore`); `load_active_rules(cwd) -> (durable_tuple, ignore_tuple) | None`; `.sdd.json` contract (`ecosystems`, `extra_durable`, `extra_ignore`). Tasks 3-5 document exactly these names/keys.
- Consumes: current hook (v0.1.1) — `_run()`/`main()` fail-open structure, turn-boundary logic, `project_relative()` (all preserved).

- [ ] **Step 1: Append the failing tests**

Append to the END of `tests/test_check_docs_updated.py` (after `test_wrapper_launcher_blocks_end_to_end`) exactly:

```python


# --- ecosystem adapters -------------------------------------------------------

def make_openspec_project(tmp_path, with_native=False):
    project = tmp_path / "project"
    (project / "openspec" / "specs").mkdir(parents=True)
    (project / "openspec" / "changes").mkdir(parents=True)
    if with_native:
        (project / "docs" / "specs").mkdir(parents=True)
    return project


def test_openspec_project_blocks_code_without_docs(tmp_path):
    project = make_openspec_project(tmp_path)
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "src" / "main.py"),
    ])
    assert_blocks(run_hook(project, transcript))


def test_openspec_specs_edit_satisfies(tmp_path):
    project = make_openspec_project(tmp_path)
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "src" / "main.py"),
        edit_line(project / "openspec" / "specs" / "payments" / "spec.md"),
    ])
    assert run_hook(project, transcript) == ""


def test_openspec_changes_edit_does_not_satisfy(tmp_path):
    # openspec/changes/ is the working layer - like docs/plans/, editing a
    # proposal or tasks file is not a durable docs update
    project = make_openspec_project(tmp_path)
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "src" / "main.py"),
        edit_line(project / "openspec" / "changes" / "add-x" / "tasks.md"),
    ])
    assert_blocks(run_hook(project, transcript))


def test_openspec_changes_only_edit_does_not_trigger(tmp_path):
    project = make_openspec_project(tmp_path)
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "openspec" / "changes" / "add-x" / "proposal.md"),
    ])
    assert run_hook(project, transcript) == ""


def test_adr_satisfies_in_openspec_project(tmp_path):
    project = make_openspec_project(tmp_path)
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "src" / "main.py"),
        edit_line(project / "docs" / "decisions" / "0001-choice.md"),
    ])
    assert run_hook(project, transcript) == ""


def test_hybrid_project_either_spec_tree_satisfies(tmp_path):
    project = make_openspec_project(tmp_path, with_native=True)
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "src" / "main.py"),
        edit_line(project / "openspec" / "specs" / "auth" / "spec.md"),
    ])
    assert run_hook(project, transcript) == ""


def test_sdd_json_forces_ecosystem(tmp_path):
    # config can arm the hook even before the spec tree exists
    project = tmp_path / "project"
    project.mkdir()
    (project / ".sdd.json").write_text(
        json.dumps({"ecosystems": ["openspec"]}), encoding="utf-8"
    )
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "src" / "main.py"),
    ])
    assert_blocks(run_hook(project, transcript))


def test_empty_ecosystems_config_disables_hook(tmp_path):
    project = make_project(tmp_path)  # has docs/specs
    (project / ".sdd.json").write_text(
        json.dumps({"ecosystems": []}), encoding="utf-8"
    )
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "src" / "main.py"),
    ])
    assert run_hook(project, transcript) == ""


def test_malformed_sdd_json_falls_back_to_detection(tmp_path):
    project = make_project(tmp_path)  # native project
    (project / ".sdd.json").write_text("{not json", encoding="utf-8")
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "src" / "main.py"),
    ])
    assert_blocks(run_hook(project, transcript))


def test_extra_durable_from_config(tmp_path):
    project = make_project(tmp_path)
    (project / ".sdd.json").write_text(
        json.dumps({"extra_durable": ["wiki/adr/"]}), encoding="utf-8"
    )
    transcript = write_transcript(tmp_path, [
        user_line(),
        edit_line(project / "src" / "main.py"),
        edit_line(project / "wiki" / "adr" / "0001-x.md"),
    ])
    assert run_hook(project, transcript) == ""
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python -m pytest tests/ -v -k "openspec or sdd_json or ecosystems_config or extra_durable or hybrid"`
Expected against the OLD hook: exactly these 6 MUST FAIL — `test_openspec_project_blocks_code_without_docs`, `test_openspec_changes_edit_does_not_satisfy`, `test_hybrid_project_either_spec_tree_satisfies`, `test_sdd_json_forces_ecosystem`, `test_empty_ecosystems_config_disables_hook`, `test_extra_durable_from_config` (either empty stdout → `json.loads("")` raises, or an unexpected block). The other 4 pass incidentally (the old hook is silent in openspec-only projects). Record the failing list as TDD evidence.

- [ ] **Step 3: Replace `hooks/check-docs-updated.py` with the full new content**

```python
#!/usr/bin/env python3
"""Stop hook for the sdd-convention plugin.

Reminds the agent to update durable docs (specs/ADRs) when a turn edited
project files outside the documentation trees without touching the durable
layer (specs or decisions).

Which trees count is ecosystem data (ECOSYSTEMS): the native convention uses
docs/specs + docs/decisions; OpenSpec projects use openspec/specs +
docs/decisions. Detection unions every ecosystem whose detect dir exists; an
optional .sdd.json at the project root forces or extends it.

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

ECOSYSTEMS = {
    "native": {
        "detect": "docs/specs",
        "durable": ("docs/specs/", "docs/decisions/"),
        "ignore": ("docs/",),
    },
    "openspec": {
        "detect": "openspec/specs",
        "durable": ("openspec/specs/", "docs/decisions/"),
        "ignore": ("openspec/", "docs/"),
    },
}

REASON = (
    "SDD convention check: this turn edited project files outside the "
    "documentation trees but did not update the durable docs layer (specs or "
    "ADRs). Invoke the sdd-finalize skill now and either (a) update the "
    "canonical spec and/or write an ADR for what changed, or (b) if nothing "
    "durable changed (pure refactor, typo, tooling), state that explicitly to "
    "the user in one sentence. Do not fabricate doc updates."
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
    with open(transcript_path, encoding="utf-8", errors="replace") as fh:
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


def _as_prefix(p):
    """Normalize a user-supplied path prefix to forward-slash + trailing /."""
    p = p.replace("\\", "/").lstrip("./")
    return p if p.endswith("/") else p + "/"


def load_active_rules(cwd):
    """Resolve (durable, ignore) prefix tuples for this project, or None when
    no ecosystem applies (the hook stays silent).

    Auto-detection unions every ecosystem whose detect directory exists. An
    optional .sdd.json at the project root can force the ecosystem list
    ({"ecosystems": [...]}) and extend the sets ("extra_durable",
    "extra_ignore"). A malformed config is ignored - fail open to detection.
    """
    forced = None
    extra_durable, extra_ignore = [], []
    config_path = os.path.join(cwd, ".sdd.json")
    if os.path.isfile(config_path):
        try:
            with open(config_path, encoding="utf-8") as fh:
                config = json.load(fh)
        except (OSError, ValueError):
            config = None
        if isinstance(config, dict):
            raw = config.get("ecosystems")
            if isinstance(raw, list):
                forced = [n for n in raw if n in ECOSYSTEMS]
            extra_durable = [
                p for p in config.get("extra_durable") or []
                if isinstance(p, str) and p.strip()
            ]
            extra_ignore = [
                p for p in config.get("extra_ignore") or []
                if isinstance(p, str) and p.strip()
            ]
    if forced is not None:
        names = forced
    else:
        names = [
            name for name, eco in ECOSYSTEMS.items()
            if os.path.isdir(os.path.join(cwd, *eco["detect"].split("/")))
        ]
    if not names and not extra_durable:
        return None
    durable = {p for name in names for p in ECOSYSTEMS[name]["durable"]}
    durable.update(_as_prefix(p) for p in extra_durable)
    ignore = {p for name in names for p in ECOSYSTEMS[name]["ignore"]}
    ignore.update(_as_prefix(p) for p in extra_ignore)
    ignore.update(durable)
    return tuple(durable), tuple(ignore)


def _run():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(data, dict) or data.get("stop_hook_active"):
        return 0

    cwd = data.get("cwd") or os.getcwd()
    rules = load_active_rules(cwd)
    if rules is None:
        return 0  # project has not opted into the convention
    durable, ignore = rules

    transcript_path = data.get("transcript_path")
    if not transcript_path or not os.path.isfile(transcript_path):
        return 0

    try:
        edited = edited_paths_in_last_turn(transcript_path)
    except OSError:
        return 0

    rels = [r for r in (project_relative(p, cwd) for p in edited) if r]
    code_edits = [r for r in rels if not r.startswith(ignore)]
    doc_edits = [r for r in rels if r.startswith(durable)]

    if code_edits and not doc_edits:
        print(json.dumps({"decision": "block", "reason": REASON}))
    return 0


def main():
    try:
        return _run()
    except Exception:
        return 0  # fail open: this hook is a reminder, never an error source


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the whole suite to verify all pass**

Run: `python -m pytest tests/ -v`
Expected: **28/28 PASS**, no warnings. The 18 pre-existing tests must be untouched by your diff (verify with `git diff tests/ | grep "^-" | grep -v "^---"` → empty).

- [ ] **Step 5: Commit**

```bash
git add hooks/check-docs-updated.py tests/test_check_docs_updated.py
git commit -m "feat: ecosystem adapters in Stop hook (native + openspec, .sdd.json override)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: OpenSpec variant of the CLAUDE.md rules block

**Files:**
- Create: `scaffold/CLAUDE-openspec.md`

**Interfaces:**
- Produces: `scaffold/CLAUDE-openspec.md` with the exact markers `<!-- sdd-convention:start -->` / `<!-- sdd-convention:end -->` — Task 3's command references this exact path.

- [ ] **Step 1: Write `scaffold/CLAUDE-openspec.md` — full content**

```markdown
# Project memory - READ THIS FIRST

<!-- sdd-convention:start -->
> This section is managed by the sdd-convention plugin (OpenSpec variant). It
> tells any agent **where the truth lives** and **how to tell what is
> current**. Do not repeat spec content here; point to it.

## Single source of truth

The **only** canonical specs live in `openspec/specs/` (OpenSpec format, one
capability per folder). A change under `openspec/changes/` is a proposal
about the future, and anything under `openspec/changes/archive/` is history -
neither is current truth.

Authority order when sources conflict:

1. `openspec/specs/*`  - what the system MUST do today
2. The code  - what it actually does today
3. `docs/decisions/*` (ADRs)  - WHY it changed from A to B
4. `openspec/changes/archive/*`  - completed change history. Ignore by default.

If a spec and the code diverge, the spec wins: align the code and record the
reconciliation in an ADR. Never silently edit a spec to match drifted code.

## How to find what is current (without reading everything)

- `openspec/specs/<capability>/spec.md` - current truth per capability
  (use `openspec list` / `openspec validate` when the CLI is available)
- `docs/decisions/README.md` - decision log (the "from A to B and why")
- `openspec/changes/` - work in progress. Ephemeral.

## Rules for agents editing documentation

1. **Spec changes go through the OpenSpec flow** (propose -> apply ->
   archive). Do not hand-edit `openspec/specs/` outside that flow.
2. **Any decision, or contradiction of a previous decision, requires an ADR**
   in `docs/decisions/` - with `supersedes: ADR-XXXX` when it replaces one.
   The ADR is the only place where the contradiction may live.
3. **Never delete an ADR.** Mark it `status: superseded` and write the new
   one.
4. **Changes are disposable.** After archiving a change, the durable "why"
   graduates to an ADR; the archived change folder is a paper trail, not a
   source of truth.

## Finishing work

At the end of any task that changed behavior:

- Behavior change - update the spec via the OpenSpec change flow.
- Architecture choice / trade-off / contradiction - write an **ADR** in
  `docs/decisions/`.
- Nothing durable changed - say so explicitly in one sentence.
<!-- sdd-convention:end -->
```

- [ ] **Step 2: Verify the markers**

Run: `python -c "import pathlib; t = pathlib.Path('scaffold/CLAUDE-openspec.md').read_text(encoding='utf-8'); assert '<!-- sdd-convention:start -->' in t and '<!-- sdd-convention:end -->' in t; print('markers ok')"`
Expected: `markers ok`

- [ ] **Step 3: Commit**

```bash
git add scaffold/CLAUDE-openspec.md
git commit -m "feat: add OpenSpec variant of the CLAUDE.md rules block

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Hybrid /sdd-init command

**Files:**
- Modify: `commands/sdd-init.md` (full replacement below)

**Interfaces:**
- Consumes: `scaffold/CLAUDE-openspec.md` (Task 2), `.sdd.json` key names from Task 1 (`ecosystems`, `extra_durable`, `extra_ignore`).

- [ ] **Step 1: Replace `commands/sdd-init.md` with — full content**

```markdown
---
description: Set up the SDD convention in this project (docs structure, CLAUDE.md rules block, hygiene linter) - adapts to OpenSpec projects
argument-hint: [docs language, e.g. "en" or "pt-BR"]
---

Set up the SDD documentation convention in the current project. Read the
sdd-source-of-truth skill first if you have not this session. Every step is
idempotent: when a piece already exists, leave it untouched and report it.

The plugin's assets live at ${CLAUDE_PLUGIN_ROOT} (scaffold/ and templates/).
If that variable did not expand, locate the sdd-convention plugin directory
under ~/.claude/plugins/.

0. Detect the ecosystem: if the project has an `openspec/` directory
   (OpenSpec - specs live in `openspec/specs/`), follow the OPENSPEC PATH.
   Otherwise follow the NATIVE PATH.

## NATIVE PATH

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

## OPENSPEC PATH (hybrid mode)

The Spec layer already lives in `openspec/specs/` - creating `docs/specs/`
would produce two competing canonical trees, the exact failure mode this
convention prevents. Set up only the Decision layer and the rules:

1. Docs language: use $ARGUMENTS if given; otherwise detect; otherwise ask.
2. Create only, if missing:
   - docs/decisions/README.md  (from ${CLAUDE_PLUGIN_ROOT}/scaffold/docs/decisions/README.md)
   - scripts/check-docs.py     (from ${CLAUDE_PLUGIN_ROOT}/scaffold/scripts/check-docs.py)
   Do NOT create docs/specs/, docs/plans/, or docs/_archive/ - the OpenSpec
   trees (openspec/specs/, openspec/changes/) play those roles.
3. CLAUDE.md rules block: same merge logic as the native path, but using
   ${CLAUDE_PLUGIN_ROOT}/scaffold/CLAUDE-openspec.md as the source file.
4. Do not write .sdd.json - the Stop hook auto-detects openspec/specs/.
   Mention in the report that an optional .sdd.json at the project root
   ({"ecosystems": [...], "extra_durable": [...], "extra_ignore": [...]})
   can override detection.

## BOTH PATHS - finish

5. If the chosen docs language is not English, translate the copied index
   READMEs and the CLAUDE.md block body into it. Keep frontmatter keys and
   status values in English - the linter depends on them.
6. Run `python scripts/check-docs.py docs` and show the output.
7. Report: ecosystem detected, what was created, what already existed, and
   suggest adding `python scripts/check-docs.py docs` to CI.
```

- [ ] **Step 2: Commit**

```bash
git add commands/sdd-init.md
git commit -m "feat: make /sdd-init ecosystem-aware (hybrid mode for OpenSpec projects)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: Ecosystem-aware skills

**Files:**
- Modify: `skills/sdd-source-of-truth/SKILL.md`
- Modify: `skills/sdd-finalize/SKILL.md`
- Modify: `skills/sdd-retrofit/SKILL.md`

**Interfaces:**
- Consumes: adapter table values and `.sdd.json` keys from Task 1; the OpenSpec flow names (`propose -> apply -> archive`).
- Constraint: every `description` stays under 1024 characters (verify per file).

- [ ] **Step 1: Edit `skills/sdd-source-of-truth/SKILL.md`**

Replace the frontmatter `description:` line with:

```
description: Use when reading or editing anything under docs/specs/, docs/decisions/, docs/_archive/, or openspec/specs/, or when determining what the system's current behavior should be, in a project using the SDD convention (has docs/specs/ or openspec/specs/). Defines the 3-layer model, authority order, ecosystem mapping, frontmatter schemas, and the four lifecycle rules.
```

Insert AFTER the 3-layer table (after the line `| **Decision** | Why did A become B?      | Immutable - append-only         | \`docs/decisions/\` |`) and BEFORE `## Authority order`:

```markdown

## Ecosystems

The three layers are the invariant; where the Spec layer lives is ecosystem
data. The Decision layer is ALWAYS `docs/decisions/`, in every ecosystem.

| Ecosystem | Spec layer | Working layer | Decision layer |
|---|---|---|---|
| native | `docs/specs/` | `docs/plans/` | `docs/decisions/` |
| OpenSpec | `openspec/specs/` | `openspec/changes/` | `docs/decisions/` |

- The authority order below is identical in every ecosystem - substitute the
  Spec-layer path (in OpenSpec: item 1 is `openspec/specs/*`, item 4 is
  `openspec/changes/archive/*`).
- OpenSpec specs use OpenSpec's own format (Requirements/Scenarios, validated
  by `openspec validate`) - the frontmatter schemas and lifecycle rules below
  govern the native tree. In OpenSpec, behavior retirement is `REMOVED
  Requirements` via a change, not `docs/_archive/`.
- An optional `.sdd.json` at the project root overrides detection:
  `{"ecosystems": ["openspec"], "extra_durable": [...], "extra_ignore": [...]}`.
```

- [ ] **Step 2: Edit `skills/sdd-finalize/SKILL.md`**

Replace the frontmatter `description:` line with:

```
description: Use when finishing a feature, plan, branch, or any task that changed code in a project using the SDD convention (has docs/specs/ or openspec/specs/) - promotes durable knowledge into specs/ADRs so documentation stays the single source of truth. Also invoke when the SDD Stop hook reports that code changed without a docs update.
```

Replace checklist item 2 (the whole numbered item starting `2. **Behavior changed?**` through `templates/spec.md\` with the next SPEC id.`) with:

```markdown
2. **Behavior changed?** Native tree: edit the canonical spec in `docs/specs/`
   **in place** - describe the present only, bump `version`, set `updated` to
   today; if no spec covers this domain yet, create one from
   `${CLAUDE_PLUGIN_ROOT}/templates/spec.md` with the next SPEC id. OpenSpec
   project: spec changes go through the OpenSpec flow (propose -> apply ->
   archive) - do not hand-edit `openspec/specs/`; if the change is already
   applied, verify the spec reflects the final behavior.
```

Append to the end of the `## Rules that trip agents up` list:

```markdown
- In OpenSpec projects, editing `openspec/changes/` (proposal, tasks, design)
  is working-layer activity - never a durable docs update. Durable =
  `openspec/specs/` (via the flow) and `docs/decisions/`.
```

- [ ] **Step 3: Edit `skills/sdd-retrofit/SKILL.md`**

Insert AFTER the intro paragraph (after `...becomes a wrong source\nof truth.`) and BEFORE `## Phase 1 - Inventory (no deep reading)`:

```markdown

## Phase 0 - Detect the ecosystem

If the project has `openspec/specs/`, the canonical Spec layer is OpenSpec's:
consolidate INTO `openspec/specs/` capabilities and never create a parallel
`docs/specs/`. `openspec/changes/archive/` entries are ADR candidates -
distill each archived change that carried a real decision into a short ADR in
`docs/decisions/`. Everything else in this playbook applies unchanged, with
`openspec/specs/` substituted for `docs/specs/`.
```

Replace the first sentence of Phase 4 (`Finish exactly like /sdd-init: copy any missing scaffold pieces (index`
`READMEs, \`docs/plans/active|archive/\`, \`docs/_archive/\`,`
`\`scripts/check-docs.py\`), merge the CLAUDE.md rules block, ask about the`
`project docs language, and offer wiring \`check-docs.py\` into CI.`) with:

```markdown
Finish exactly like /sdd-init, which is ecosystem-aware: native projects get
the full scaffold (index READMEs, `docs/plans/active|archive/`,
`docs/_archive/`, `scripts/check-docs.py`); OpenSpec projects get hybrid mode
(only `docs/decisions/` + linter + the OpenSpec rules block). Merge the
CLAUDE.md rules block, ask about the project docs language, and offer wiring
`check-docs.py` into CI.
```

- [ ] **Step 4: Verify description lengths**

Run (PowerShell), for each of the three SKILL.md files:
`$m = Get-Content <path> -Raw; ([regex]::Match($m, '(?s)description: (.+?)\n---').Groups[1].Value.Length)`
Expected: each below 1024.

- [ ] **Step 5: Commit**

```bash
git add skills/
git commit -m "feat: make skills ecosystem-aware (OpenSpec mapping, finalize branch, retrofit Phase 0)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: README + version 0.2.0

**Files:**
- Modify: `README.md` (three edits below)
- Modify: `.claude-plugin/plugin.json` (version)
- Modify: `.claude-plugin/marketplace.json` (version)

**Interfaces:**
- Consumes: adapter table and `.sdd.json` contract from Task 1; hybrid init behavior from Task 3.

- [ ] **Step 1: Edit README — hook opt-in line**

Replace:

```markdown
The Stop hook only acts in projects that have a `docs/specs/` directory -
installing the plugin globally does not affect other projects.
```

with:

```markdown
The Stop hook only acts in projects with a recognized spec tree
(`docs/specs/`, or `openspec/specs/` in OpenSpec projects) - installing the
plugin globally does not affect other projects.
```

- [ ] **Step 2: Edit README — insert the Ecosystem adapters section**

Insert AFTER the closing fence of the "Project layout after /sdd-init" tree block and BEFORE `## Using it with other agents (Codex, Cursor, ...)`:

````markdown
## Ecosystem adapters

The three layers are the invariant; where the Spec layer lives is adapter
data. v0.2.0 ships two adapters, detected automatically (union - hybrid
projects get both):

| Adapter | Detected by | Durable (satisfies the hook) | Working (ignored) |
|---|---|---|---|
| `native` | `docs/specs/` | `docs/specs/`, `docs/decisions/` | `docs/plans/` |
| `openspec` | `openspec/specs/` | `openspec/specs/`, `docs/decisions/` | `openspec/changes/` |

The Decision layer (ADRs) is always `docs/decisions/` - it is this plugin's
tool-neutral contribution; [OpenSpec](https://github.com/Fission-AI/OpenSpec)
has no equivalent. In an OpenSpec project, `/sdd-init` runs in hybrid mode:
it creates only `docs/decisions/` + the linter + an OpenSpec-flavored rules
block (never a second canonical spec tree), and spec changes keep flowing
through OpenSpec's propose -> apply -> archive.

An optional `.sdd.json` at the project root overrides detection:

```json
{
  "ecosystems": ["openspec"],
  "extra_durable": ["wiki/adr/"],
  "extra_ignore": ["sandbox/"]
}
```

`ecosystems` forces the adapter set (an empty list disables the hook for the
project); `extra_*` append path prefixes; a malformed file falls back to
detection. Adding a future adapter (Spec Kit, ...) is one entry in the hook's
`ECOSYSTEMS` table.

````

- [ ] **Step 3: Edit README — prior art**

Insert after the `- [GitHub Spec Kit]...` bullet (before the `- [AGENTS.md]...` bullet):

```markdown
- [OpenSpec](https://github.com/Fission-AI/OpenSpec) - lightweight SDD change
  flow (propose -> apply -> archive); the `openspec` adapter maps its `specs/`
  tree as the Spec layer and adds the Decision layer it lacks.
```

- [ ] **Step 4: Bump versions to 0.2.0**

In `.claude-plugin/plugin.json`: `"version": "0.1.0"` → `"version": "0.2.0"`.
In `.claude-plugin/marketplace.json`: `"version": "0.1.0"` → `"version": "0.2.0"`.

Run: `python -m json.tool .claude-plugin/plugin.json && python -m json.tool .claude-plugin/marketplace.json`
Expected: both parse, both show 0.2.0.

- [ ] **Step 5: Commit**

```bash
git add README.md .claude-plugin/
git commit -m "docs: document ecosystem adapters; bump version to 0.2.0

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: Dogfood finalize (SPEC-001 v2, ADR-0005, indexes, archive plans)

**Files:**
- Modify: `docs/specs/001-plugin-architecture.md`
- Create: `docs/decisions/0005-ecosystems-are-adapter-data.md`
- Modify: `docs/specs/README.md` (index row)
- Modify: `docs/decisions/README.md` (log row)
- Move: `docs/plans/active/2026-07-19-openspec-ecosystem-adapters-design.md` → `docs/plans/archive/`
- Move: `docs/plans/active/2026-07-19-openspec-ecosystem-adapters-plan.md` → `docs/plans/archive/`

**Interfaces:**
- Consumes: everything shipped in Tasks 1-5. This is our own convention's mandatory finalize step.

- [ ] **Step 1: Update SPEC-001 — apply these exact changes**

Frontmatter: `version: 1` → `version: 2` (keep `updated: 2026-07-19`).

In `### Enforcement`, replace item 9's phrase `edited project files outside \`docs/\` without also editing \`docs/specs/\` or \`docs/decisions/\`` with `edited project files outside the recognized documentation trees without also editing the durable layer (see Ecosystem adapters)`.

Insert a new subsection AFTER item 12 (the ADR-0003 item) and BEFORE `### Assets and tooling`:

```markdown
### Ecosystem adapters

12a. Which trees count as documentation is ecosystem data in the hook's
    `ECOSYSTEMS` table. Shipped adapters: `native` (detect `docs/specs`;
    durable `docs/specs/` + `docs/decisions/`; ignore `docs/`) and `openspec`
    (detect `openspec/specs`; durable `openspec/specs/` + `docs/decisions/`;
    ignore `openspec/` + `docs/`). Detection unions every detected adapter.
    (ADR-0005)
12b. The Decision layer is ALWAYS `docs/decisions/`, in every ecosystem.
    (ADR-0005)
12c. An optional `.sdd.json` at the project root overrides detection with
    keys `ecosystems` (forces the set; empty list disables the hook),
    `extra_durable`, `extra_ignore`. A malformed file falls back to
    detection. (ADR-0005)
12d. `/sdd-init` is ecosystem-aware: in OpenSpec projects it runs hybrid mode
    (only `docs/decisions/` + linter + `scaffold/CLAUDE-openspec.md` rules
    block; never a second canonical spec tree). `sdd-retrofit` consolidates
    into `openspec/specs/` in OpenSpec projects.
```

In `## Related decisions`, append: `- ADR-0005 - Ecosystems are descriptive adapter data; the Decision layer is fixed (accepted)`.

In `## Changelog`, add a row above version 1: `| 2       | 2026-07-19 | Ecosystem adapters: native + openspec, .sdd.json override (ADR-0005). |`

- [ ] **Step 2: Write `docs/decisions/0005-ecosystems-are-adapter-data.md` — full content**

```markdown
---
id: ADR-0005
title: Ecosystems are descriptive adapter data; the Decision layer is fixed
status: accepted
date: 2026-07-19
supersedes: null
superseded_by: null
---

# ADR-0005 - Ecosystems are descriptive adapter data; the Decision layer is fixed

## Context

Users do SDD with different spec/working ecosystems (the native convention,
OpenSpec today; Spec Kit and others tomorrow). The plugin's value - lifecycle
governance, the ADR layer, deterministic enforcement - is ecosystem-neutral;
only the Spec layer's location and format vary. Options considered: adapters
as Python modules (dynamic loading), everything via a config file, or
descriptive data entries.

## Decision

Each ecosystem is a data entry ({detect, durable, ignore}) in the hook's
ECOSYSTEMS table - no adapter code. Detection unions every ecosystem whose
detect directory exists; an optional .sdd.json ("ecosystems",
"extra_durable", "extra_ignore") forces or extends it, failing open to
detection when malformed. The Decision layer is ALWAYS docs/decisions/, in
every ecosystem. /sdd-init in an OpenSpec project runs hybrid mode and never
creates a second canonical spec tree.

## Consequences

- Adding an ecosystem (Spec Kit, ...) is one dict entry + docs + tests - no
  architecture.
- The hook stays a single stdlib file (ADR-0004 holds) and fail-open
  (ADR-0002 holds).
- OpenSpec projects gain the ADR layer and enforcement without leaving their
  propose -> apply -> archive flow; openspec/changes/ never satisfies the
  hook (working layer).
- Native-mode behavior is unchanged from v0.1.x.
```

- [ ] **Step 3: Update the indexes**

`docs/specs/README.md`: in the index table, change the SPEC-001 row to `| SPEC-001 | Plugin architecture | active | 2       | 2026-07-19 |`.

`docs/decisions/README.md`: append to the decision log table: `| ADR-0005 | Ecosystems are adapter data; Decision layer fixed | accepted | -          | 2026-07-19 |`

- [ ] **Step 4: Archive both working docs**

```bash
git mv docs/plans/active/2026-07-19-openspec-ecosystem-adapters-design.md docs/plans/archive/
git mv docs/plans/active/2026-07-19-openspec-ecosystem-adapters-plan.md docs/plans/archive/
```

- [ ] **Step 5: Run the linter**

Run: `python scripts/check-docs.py docs` — if `scripts/check-docs.py` does not exist at repo root, run `python scaffold/scripts/check-docs.py docs`.
Expected: 5 ADRs counted, zero errors, final line `OK - no hygiene violations found.`

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "docs: finalize ecosystem adapters - SPEC-001 v2, ADR-0005, archive plans

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: Release v0.2.0

**Files:** none (repo operations).

**Interfaces:**
- Consumes: all commits from Tasks 1-6; version 0.2.0 already in the manifests (Task 5).

- [ ] **Step 1: Full local validation**

Run: `python -m pytest tests/ -v && python scaffold/scripts/check-docs.py scaffold/docs && python -m json.tool .claude-plugin/plugin.json > /dev/null && python -m json.tool .claude-plugin/marketplace.json > /dev/null && echo ALL-OK`
Expected: 28/28 pass; scaffold linter OK; `ALL-OK`. Also `git status --porcelain` must be empty.

- [ ] **Step 2: Push and tag**

```bash
git push origin main
git tag v0.2.0
git push origin v0.2.0
```

- [ ] **Step 3: Verify CI**

Run: `gh run list --repo pablopupulin/sdd-convention --limit 1` (wait/poll until the run for the pushed commit completes).
Expected: `completed success`.

- [ ] **Step 4: Refresh the local install**

Run: `claude plugin marketplace update sdd-convention`
Expected: marketplace refreshed; the locally installed plugin picks up 0.2.0 (if the CLI reports an update command for the plugin itself, run it and report).

- [ ] **Step 5: Report**

Report to the controller: tag pushed, CI status, local plugin version after update.
