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
