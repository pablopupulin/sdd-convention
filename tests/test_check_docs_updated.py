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


def test_truncated_utf8_transcript_fails_open(tmp_path):
    # a transcript cut mid multi-byte sequence (flush race) must not crash the
    # hook; lines that parsed still count, so the block still fires here
    project = make_project(tmp_path)
    transcript = tmp_path / "transcript.jsonl"
    valid = (
        json.dumps(user_line()) + "\n"
        + json.dumps(edit_line(project / "src" / "main.py")) + "\n"
    ).encode("utf-8")
    transcript.write_bytes(valid + b'{"type": "user", "message": "caf\xc3')
    assert_blocks(run_hook(project, transcript))


def test_wrong_typed_stdin_fields_fail_open(tmp_path):
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps({"cwd": 5, "transcript_path": 7, "stop_hook_active": False}),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""


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
