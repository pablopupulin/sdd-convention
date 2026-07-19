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
