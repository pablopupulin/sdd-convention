# Internal audit of the sdd-convention plugin (repo state as of 2026-11-12)

Scope: every git-tracked file in `/home/user/sdd-convention` (48 files, 5,630 lines; HEAD `d836a58`, branch identical to `main`). Version 0.2.0. All 25 commits are dated 2026-07-19 (one day of work, then ~4 months without commits). No git tags exist in this clone. Sources are cited as `path:line` relative to the repo root; "[experiment]" means I ran it in a scratch directory on 2026-11-12 (Python 3.13, Linux) without touching repo files. External facts come from the Claude Code docs: [manifest reference](https://code.claude.com/docs/en/plugins-reference) and [hooks reference](https://code.claude.com/docs/en/hooks.md).

Size inventory (lines): skills 107 + 52 + 77 = 236 (about 1,600 words total); commands 67 + 8; hook 217; launcher 24; linter 119 (duplicated byte-identical in `scripts/` and `scaffold/scripts/`); tests 451 (31 tests); templates 38 + 25; README 209; SPEC-001 142; 5 ADRs (about 30-40 lines each); archived plans 3,007 lines (more than half of the repo).

## 1. What workflow/lifecycle does the plugin enforce, how is each step triggered, and what is automated vs. advisory?

### Takeaway
The plugin is a documentation-governance layer, not a full SDD workflow: it defines where truth lives (living spec / append-only ADR / disposable plan) and nudges the agent at end-of-turn to promote changes into specs/ADRs. Exactly one thing is deterministic (the Stop-hook reminder, once per turn, and only for Edit/Write-tool edits); everything else, including the linter in consumer projects, is prompt-level advice.

### Cited Findings
- Three layers by mutability: Working (`docs/plans/`, ephemeral), Spec (`docs/specs/`, living, edited in place), Decision (`docs/decisions/`, append-only) — `skills/sdd-source-of-truth/SKILL.md:12-16`, `README.md:57-61`.
- Authority order: active spec > code > ADRs > `_archive`; "the spec wins: align the code and record the reconciliation in an ADR" — `skills/sdd-source-of-truth/SKILL.md:40-49`, `scaffold/CLAUDE.md` (identical to root `CLAUDE.md`; `diff` returned no differences).
- Four lifecycle rules: specs edited in place with `version`/`updated` bump; contradiction requires a new ADR with `supersedes`; retire-never-delete (`status: archived` + `superseded_by` + move to `docs/_archive/`); plans disposable and archived on merge — `skills/sdd-source-of-truth/SKILL.md:81-94`.
- Lifecycle step to trigger mapping:
  - Project setup: `/sdd-init` command, manual, executed by the LLM following a prose recipe (no script) — `commands/sdd-init.md:6-67`.
  - Migration of legacy docs: `/sdd-retrofit` command, an 8-line wrapper that invokes the `sdd-retrofit` skill; 4 phases with approval gates — `commands/sdd-retrofit.md:6-8`, `skills/sdd-retrofit/SKILL.md:13-77`.
  - Reading/editing docs: `sdd-source-of-truth` skill, model-invoked by description match — `skills/sdd-source-of-truth/SKILL.md:3`.
  - Plan creation/execution: not provided. Delegated to external tooling ("brainstorm - worktree - plan - implement flows such as Superpowers") — `docs/plans/README.md:3-5`, `README.md:192-194`.
  - End of task: `sdd-finalize` skill (7-step checklist: list changes, update spec, write ADR, archive plan, update indexes, run linter, or declare "nothing durable changed") — `skills/sdd-finalize/SKILL.md:14-39`. Triggered by description match or by the Stop hook's block reason, which names the skill — `hooks/check-docs-updated.py:40-47`.
  - Hygiene validation: `scripts/check-docs.py`, run only if the agent follows the skill text or the user wires it into CI — `skills/sdd-finalize/SKILL.md:33-34`, `commands/sdd-init.md:66-67` ("suggest adding ... to CI").
- Deterministic pieces: (a) Stop hook; (b) the linter, but only inside this repo's own CI (`.github/workflows/ci.yml:23-26`). Nothing installs a CI job, pre-commit hook, or git hook in consumer projects; `/sdd-init` only "suggests" CI wiring (`commands/sdd-init.md:66-67`), and a PreToolUse hook on `git commit` is explicitly out of scope (`docs/specs/001-plugin-architecture.md:125`, `docs/decisions/0002-stop-hook-fails-open.md:26`).
- The hook docstring and SPEC-001 state "hard enforcement lives in CI (check-docs.py)" — `hooks/check-docs-updated.py:13-15`, `docs/specs/001-plugin-architecture.md:71-72`. The linter checks only frontmatter hygiene (see section 3); it has no notion of code changes, so the rule "code changed, therefore docs must change" is hard-enforced nowhere.
- The legitimate exit from the hook is one sentence stating nothing durable changed — `skills/sdd-finalize/SKILL.md:35-39`. The hook cannot verify that sentence; `stop_hook_active` makes the second stop pass unconditionally — `hooks/check-docs-updated.py:182-183`.
- Draft-to-active transition is undefined: `templates/spec.md:4` starts new specs at `status: draft` with `canonical: true` (line 10), while agents are told to trust only `canonical: true` + `status: active` (`skills/sdd-source-of-truth/SKILL.md:64`); no skill says when or who flips draft to active (`skills/sdd-finalize/SKILL.md:17-20` creates the spec and stops).
- The repo dogfoods the convention: one active spec, five ADRs, one archived design, three archived plans, empty `docs/plans/active/` — `docs/specs/README.md:12`, `docs/decisions/README.md:19-23`, commit `d55262c`.

### Inferences
- The actual enforced loop is "edit code with Edit/Write, get one reminder, either touch any file under a durable tree or say one sentence". Spec-first ordering (spec before code) is not enforced or even recommended; the flow is code-first with documentation promotion afterwards. This is closer to "docs-as-governance" than to Spec Kit/Kiro-style "spec, plan, tasks, implement".
- Because `/sdd-init` is a prose recipe run by the model, its result (file copies, marker merge, translation) is non-deterministic and untested.

### Gaps
- No evidence in the repo of a live end-to-end install test in a real Claude Code session (the archived design planned one: `docs/_archive/2026-07-plugin-architecture-design.md`, sections "Testes e validacao" and "Publicacao"); whether it was done is not recorded.

## 2. How does the Stop hook work in detail, and what are its blind spots?

### Takeaway
The hook is a small, well-hardened transcript scanner: it blocks once per turn when the main agent's Edit/Write/MultiEdit/NotebookEdit calls touched non-doc paths but no durable path. It is path-based only, blind to Bash and subagent edits, satisfiable by any trivial durable-tree edit, and on POSIX the launcher appears non-executable as shipped, which would make the hook never run.

### Cited Findings
- Registration: `Stop` event, shell-form command `"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd"`, timeout 30 s — `hooks/hooks.json:3-11`.
- Launcher: polyglot cmd/sh file; Windows tries `py -3` then `python`; POSIX tries `python3` then `python`; exits 0 if none — `hooks/run-hook.cmd:7-24`; LF pinned by `.gitattributes:1`.
- Algorithm (`hooks/check-docs-updated.py`):
  1. Parse stdin JSON; exit silently if invalid or `stop_hook_active` is true (lines 178-183).
  2. `cwd` from payload; resolve rules; exit silently if no ecosystem and no `extra_durable` (185-188).
  3. Read the whole transcript JSONL into memory, find the last "real user prompt" (user entry with string content or text blocks and no `tool_result`, not sidechain), collect `file_path`/`notebook_path` of `tool_use` blocks named Edit, Write, MultiEdit, NotebookEdit after it, skipping sidechain entries (25, 50-101).
  4. Make paths project-relative; paths outside `cwd` are dropped (104-117, 200).
  5. `code_edits` = paths not under any ignore prefix; `doc_edits` = paths under a durable prefix; if code edits exist and no doc edits, print `{"decision":"block","reason":...}` (201-205). Always exit 0 (209-213).
- Ecosystem table: `native` (detect `docs/specs`; durable `docs/specs/`, `docs/decisions/`; ignore `docs/`) and `openspec` (detect `openspec/specs`; durable `openspec/specs/`, `docs/decisions/`; ignore `openspec/`, `docs/`) — lines 27-38. Detection is a union of all detected ecosystems (162-166).
- `.sdd.json` keys: `ecosystems` (forces the set; unknown names filtered; empty list disables detection-based arming), `extra_durable`, `extra_ignore` (lists of string prefixes; non-list or non-string values ignored); malformed JSON falls back to detection — lines 139-174; behavior matches `docs/specs/001-plugin-architecture.md:87-93`.
- Fail-open: catch-all `except Exception: return 0` (209-213); rationale in `docs/decisions/0002-stop-hook-fails-open.md:19-34`.
- [experiment] Observed hook outputs for synthetic transcripts in a project with `docs/specs/`:
  - Code changed only through a Bash tool call (`sed -i ... src/main.py`): silent (false negative).
  - Edit of `README.md` only: blocks (false positive by the plugin's own definition of "nothing durable").
  - Edit of `.github/workflows/ci.yml` only: blocks. Edit of `tests/test_x.py` only: blocks.
  - Edit of `src/main.py` plus `docs/specs/README.md` (index only): silent (satisfied).
  - Edit of `src/main.py` plus an unrelated spec file: silent (satisfied).
  - Same code edit but payload `cwd` set to a subdirectory of the project: silent (opt-in detection fails).
  - Code edit followed by a later `type: "user"` entry with string content (simulating an injected meta/system-reminder line): silent, because the turn start moves past the edit.
- [experiment] Launcher on POSIX: all files in the repo are mode 100644 (`git ls-tree -r main` shows no other mode). Running the registered command form, `sh -c '"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd"'` and the same with `bash -c`, returned `Permission denied`, exit 126. The test suite does not catch this because it invokes `["sh", str(WRAPPER)]` — `tests/test_check_docs_updated.py:272-283`.
- Claude Code treats any hook exit code other than 0 or 2 as a "non-blocking error" and the action goes ahead; its own example tells authors to `chmod +x` hook scripts — [hooks reference](https://code.claude.com/docs/en/hooks.md).
- The Claude Code docs say hooks "that need the final assistant text of the current turn should use `last_assistant_message` on Stop ... instead of reading the transcript" — [hooks reference](https://code.claude.com/docs/en/hooks.md). The hook does not read that field, so it cannot check whether the "nothing durable changed" sentence was given.
- ADR-0002 accepts false positives deliberately: "Any file outside docs/ counts as code - a deliberately simple rule; false positives are cheap" — `docs/decisions/0002-stop-hook-fails-open.md:32-34`.

### Inferences
- Likely critical defect: on macOS/Linux the Stop hook probably never fires for marketplace installs (git clone preserves mode 644, shell-form execution needs the exec bit, exit 126 is swallowed as a non-blocking error). The fail-open design hides this from users. Fix candidates: commit the launcher as 100755, or register `sh "${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd"`-style / exec-form commands. This needs confirmation in a live session; I verified the shell behavior, not Claude Code's runner.
- False negatives by construction: Bash-driven changes (sed, codegen, formatters, `git mv`, package installs, migrations); edits made by subagents (sidechain entries are skipped at lines 54 and 87, and the plugin's recommended companion, Superpowers subagent-driven development, does most edits in subagents); edits by MCP tools or tools with other names; multi-turn features (only the last turn counts, so code in turn 1 and "ok thanks" in turn 2 never triggers); projects where the session cwd is a package subdirectory (monorepos).
- False positives by construction: README, CI config, tests, lockfiles, formatting. Each costs one extra model turn. There is no built-in ignore list; users must hand-write `extra_ignore`.
- Trivially satisfiable: touching any path under a durable prefix (even the index README or an unrelated spec) silences the hook; there is no check that the spec `version`/`updated` changed or that the doc relates to the code.
- The reminder fires at every qualifying turn end, not at task/branch end, which conflicts with "promote at merge" (`docs/plans/README.md:18`) and pushes agents toward per-turn spec churn or habitual "nothing durable changed" replies.
- Reading and JSON-parsing the full transcript on every Stop scales linearly with session length; fine for typical sessions, untested for very large ones.

### Gaps
- Whether real Claude Code transcripts contain string-content `type: "user"` entries mid-turn (meta messages, compaction summaries, hook feedback) was not verified against a real transcript; the test fixtures are synthetic (`tests/test_check_docs_updated.py:17-53`).
- Windows behavior was not run here; it is covered only by the CI matrix (`.github/workflows/ci.yml:13`).

## 3. What does the linter check and not check, and is it wired into CI / pre-commit for consumers?

### Takeaway
`check-docs.py` is a 119-line stdlib frontmatter checker with five nominal rules, two of which do not behave as documented, and a parser bug that makes the plugin's own templates fail or evade it. It is not wired into anything in consumer projects, and it has zero unit tests.

### Cited Findings
- Documented rules: duplicate active spec id; `superseded`/`archived` without `superseded_by`; ADR `supersedes` target missing or not superseded; duplicate ADR id; missing frontmatter or missing `id`/`status` — `scripts/check-docs.py:8-13`.
- Run against this repo: "Checked 7 docs (2 specs, 5 ADRs). OK", exit 0 [experiment]. The three archived plans (3,007 lines) are skipped because they have no frontmatter.
- Bug: inline YAML comments are not stripped (`scripts/check-docs.py:32-43`). [experiment] An ADR created verbatim from `templates/adr.md` (line 6: `supersedes: null      # ADR id this decision replaces, if any`) fails with `supersedes 'null      # ADR id this decision replaces, if any' which does not exist`, exit 1.
- Same bug, opposite direction: [experiment] two specs with `id: SPEC-001` and `status: active   # comment` are not reported as duplicates (exit 0), because status is compared as the literal string `active` (line 77). The templates and the skill's schema examples all carry such comments on `status` — `templates/spec.md:4`, `templates/adr.md:4`, `skills/sdd-source-of-truth/SKILL.md:58,72`.
- Docstring rule 5 ("Missing frontmatter") is not implemented: files without frontmatter are silently dropped at `scripts/check-docs.py:51-53`. [experiment] A frontmatter-less file in `docs/specs/` produced no error.
- Docstring rule 3 says the linter "fails" when the superseded target is not marked superseded; the code only warns — `scripts/check-docs.py:101-105`; [experiment] exit 0 with a `[warn]`.
- [experiment] Not detected (all exit 0): invalid status value (`status: banana`); an `active` spec located in `docs/_archive/`; an `archived` spec still in `docs/specs/`; `superseded_by` pointing to a non-existent id (spec or ADR); spec `supersedes` targets; duplicate spec ids when not both active.
- Not checked at all (by code reading): `canonical`, `version`, `updated`, `owner`, `date` fields; index tables in `docs/specs/README.md` / `docs/decisions/README.md` vs. actual files; filename/id numbering; "previously X" history narration in specs; stale plans in `docs/plans/active/`; links between specs and ADRs; anything in `openspec/` (explicitly out of scope: `docs/plans/archive/2026-07-19-openspec-ecosystem-adapters-design.md:122`).
- No `--strict`, JSON output, or autofix; a UTF-8 BOM would make `startswith("---")` fail and the file be skipped silently (line 22, by code reading).
- Consumer wiring: `/sdd-init` copies the script and suggests CI (`commands/sdd-init.md:28,50,66-67`); `sdd-retrofit` "offers" CI wiring (`skills/sdd-retrofit/SKILL.md:75-76`). No workflow file, pre-commit config, or git hook is shipped in `scaffold/`.
- The linter is duplicated (`scripts/check-docs.py` and `scaffold/scripts/check-docs.py`, byte-identical today) with no CI check that they stay in sync; copies in consumer projects are never updated by plugin upgrades (`/sdd-init` skips files that exist: `commands/sdd-init.md:8,22-23`).
- Instructions call `python scripts/check-docs.py` (`skills/sdd-finalize/SKILL.md:34`), while the hook launcher prefers `python3` (`hooks/run-hook.cmd:22`); on systems with only `python3` the documented command fails.

### Inferences
- The inline-comment bug means the first ADR an agent writes from the shipped template is likely to fail the linter with a confusing message, or (for specs) the main anti-duplication rule silently does nothing. This directly undermines the "machine-readable frontmatter" claim (`README.md:75-78`).
- In OpenSpec hybrid mode the linter only ever sees `docs/decisions/`, so its value there is limited to ADR chain checks.

### Gaps
- None material; behavior was verified by execution.

## 4. Quality of the skills and commands as prompts; are there evals?

### Takeaway
The skills are short, clear, and consistent with each other, with good "Use when" descriptions, but they are thin on authoring guidance and edge cases, were never pressure-tested or evaluated, and contain a few gaps that will produce inconsistent agent behavior.

### Cited Findings
- `sdd-source-of-truth` (107 lines, ~640 words): description lists concrete path triggers plus "when determining what the system's current behavior should be" — `skills/sdd-source-of-truth/SKILL.md:3`. Content: layer table, ecosystem table, authority order, two frontmatter schemas, four rules, hygiene.
- `sdd-finalize` (52 lines, ~430 words): description triggers on finishing work and on the hook message — `skills/sdd-finalize/SKILL.md:3`; includes a "Rules that trip agents up" section (41-52).
- `sdd-retrofit` (77 lines, ~520 words): "Use only when the user runs /sdd-retrofit" — `skills/sdd-retrofit/SKILL.md:3`; context-economy rules (dates only, first ~20 lines) at 24-29; approval gates at 33-39 and 50-51.
- `${CLAUDE_PLUGIN_ROOT}` in skill and command bodies is valid: the docs state the variable resolves "anywhere in the Markdown body" of skill, command, and agent content — [manifest reference](https://code.claude.com/docs/en/plugins-reference). The fallback text in `commands/sdd-init.md:10-12` is therefore unnecessary on current versions.
- The docs describe `commands/` as "Flat Markdown command files. Prefer `skills/` for new plugins" — [manifest reference](https://code.claude.com/docs/en/plugins-reference). The plugin ships both a `sdd-retrofit` command and a `sdd-retrofit` skill.
- Claude Code has a plugin eval facility (`claude plugin eval`, default `evals/` directory, `experimental.evals` manifest key) — [manifest reference](https://code.claude.com/docs/en/plugins-reference). The repo has no `evals/` directory and no skill tests; a grep of the archived plans for eval/pressure/baseline testing of skills found nothing.
- Missing or under-specified cases in the skill text:
  - No guidance on how to write a good requirement (no EARS, Given/When/Then, acceptance criteria, non-functional requirements); the template says only "Numbered requirements work well" — `templates/spec.md:24`.
  - No definition of "domain" or of when to split/merge specs, though "one canonical spec per domain" is a core rule — `skills/sdd-finalize/SKILL.md:45`.
  - Draft vs. active lifecycle undefined (see section 1).
  - Spec-vs-code divergence: "the spec wins: align the code" (`SKILL.md:47-49`) has no carve-out for the common case where the code is right and the spec is stale; the only sanctioned path is an ADR.
  - ADR immutability vs. required edits: rules say append-only, yet superseding requires editing the old ADR's `status`/`superseded_by`; the allowed mutation is implied, not stated — `skills/sdd-source-of-truth/SKILL.md:85-88`, `docs/decisions/README.md:10-12`.
  - Archived specs reuse the active spec's id with `superseded_by: SPEC-001@active` (`scaffold/docs/_archive/2026-01-example-payments-v1.md:2,9`, `docs/_archive/2026-07-plugin-architecture-design.md`); the `@active` notation is not defined in any skill or schema.
  - The Changelog table in the spec template (`templates/spec.md:34-38`) sits in tension with "a spec never narrates history" (`SKILL.md:100-101`); no skill explains the distinction.
  - No instruction about what to do when a plan exists outside `docs/plans/active/` (e.g., Superpowers' default plan locations), or about bugs, hotfixes, or multi-spec changes.
  - `sdd-finalize` step 1 relies on "your own edits this session and `git diff` if available" (`:14-16`); nothing covers work spread over several sessions or branches.
- `/sdd-init` copies `docs/specs/README.md` and `docs/decisions/README.md` from the scaffold but forbids copying the example files (`commands/sdd-init.md:22-30`); those READMEs contain index rows for the examples — `scaffold/docs/specs/README.md:12` ("SPEC-001 | Example module"), `scaffold/docs/decisions/README.md:19-20`. No step tells the agent to clear those rows, so a fresh project starts with an index pointing at non-existent docs.
- `/sdd-init` step numbering restarts and collides ("0", then 1-3 / 1-4 per path, then 5-7) — `commands/sdd-init.md:14-67`.
- README advertises `/sdd-init` and `/sdd-retrofit` (`README.md:33-34`) while SPEC-001 gives the namespaced form `/sdd-convention:<name>` (`docs/specs/001-plugin-architecture.md:50`).
- SPEC-001 item 6 ("description stays under 1024 characters", `:48`) is not checked by CI.

### Inferences
- Descriptions follow the "Use when ..." trigger style and should trigger reasonably on doc-path work; `sdd-finalize` triggering "when finishing ... any task that changed code" depends on the model noticing task completion, which is exactly what the hook was added to compensate for. With the hook possibly dead on POSIX (section 2), finalize depends on the CLAUDE.md block alone.
- The CLAUDE.md managed block (54 lines) duplicates most of `sdd-source-of-truth`; because CLAUDE.md is always in context, the skill adds mainly the schemas and ecosystem table.
- The duplicate command/skill named `sdd-retrofit` may surface as two entries or a name clash in the slash menu; not verified.

### Gaps
- No empirical data on trigger accuracy or compliance (no evals, no transcripts). Any claim about how well the skills work in practice is unverified.

## 5. Test coverage: what is tested, what is not?

### Takeaway
Only the Stop hook's Python logic is tested (31 subprocess-level tests, all passing); the linter, skills, commands, scaffold merge logic, manifests' semantics, and the launcher's real invocation path are untested.

### Cited Findings
- `python3 -m pytest tests -q`: 31 passed in 1.08 s [experiment, after installing pytest]. `python3 -m unittest discover` finds 0 tests (pytest-style functions only).
- Covered scenarios (`tests/test_check_docs_updated.py:106-451`): block on code without docs; pass with spec or ADR edit; plan edits do not satisfy; docs-only; no edits; `stop_hook_active`; project not opted in; edits outside project; only current turn; tool_result lines do not start a turn; NotebookEdit; noise/malformed lines; malformed stdin; missing transcript; truncated UTF-8; wrong-typed stdin; launcher end-to-end; 7 OpenSpec/hybrid cases; 7 `.sdd.json` cases.
- Not covered: Bash-based edits, subagent/sidechain edits, cwd in a subdirectory, injected user-type entries, relative `file_path`, Windows path case/drive handling beyond the CI matrix, large transcripts, executable-bit invocation of the launcher (test uses `sh <file>`: `:281-282`).
- Linter: no unit tests. CI runs it only on two clean trees (`scaffold/docs`, `docs`) — `.github/workflows/ci.yml:23-26`; no negative fixtures, so the bugs in section 3 pass CI.
- CI: Ubuntu + Windows, Python 3.12 only; JSON syntax checks of three JSON files via `json.tool` — `.github/workflows/ci.yml:13,18,27-32`. `claude plugin validate .` is listed under Development (`README.md:204`) but is not in CI. No macOS runner, no sync check between the two linter copies, no check that `scaffold/CLAUDE.md` equals root `CLAUDE.md`, no version-consistency check between `plugin.json` and `marketplace.json`.
- The docs note that a `CLAUDE.md` at the plugin root "isn't loaded as context, and `claude plugin validate` warns when it finds one" — [manifest reference](https://code.claude.com/docs/en/plugins-reference). This repo has a root `CLAUDE.md` (dogfooding), so `claude plugin validate --strict` would presumably fail.

### Inferences
- The test suite reflects careful hardening of one component and no testing of the rest; the two highest-impact defects found in this audit (launcher exec bit, inline-comment parsing) sit exactly in the untested seams.

### Gaps
- `claude plugin validate .` was not run (CLI not exercised in this audit), so manifest validity under the current validator is unconfirmed.

## 6. Which agents/platforms and ecosystems are supported?

### Takeaway
Real support is Claude Code only (and, pending the launcher issue, possibly Windows-only for the hook). Other agents get a manual copy-the-skills recipe with no enforcement; ecosystems are native and OpenSpec; Spec Kit, Kiro, and BMAD are not supported.

### Cited Findings
- Claude Code: marketplace + plugin in one repo (`.claude-plugin/marketplace.json:8-18` with `source: "."`, `.claude-plugin/plugin.json`); rationale in `docs/decisions/0001-repo-is-marketplace-and-plugin.md`.
- Other agents (Codex, Cursor, ...): README section tells users to copy `skills/` manually and paste a rules block plus a "Finishing work" paragraph into `AGENTS.md`; "other agents do not run the Stop hook" — `README.md:152-171`; "Hooks are Claude Code-only; elsewhere enforcement is instructional" — `docs/specs/001-plugin-architecture.md:117-120`.
- `/sdd-init` handles `AGENTS.md` only as an alternative target for the same block when the project "uses AGENTS.md instead of CLAUDE.md" — `commands/sdd-init.md:38-39`. No generation for Cursor rules, Gemini, Copilot instructions, Windsurf, or Kiro steering files; no installer script or npm/pip package.
- Skills reference `${CLAUDE_PLUGIN_ROOT}/templates/...` (`skills/sdd-finalize/SKILL.md:20,25`, `skills/sdd-retrofit/SKILL.md:55,58`, `skills/sdd-source-of-truth/SKILL.md:78-79`); this variable is a Claude Code plugin feature ([manifest reference](https://code.claude.com/docs/en/plugins-reference)), and `templates/` lives outside `skills/`, so the "copy the skills/ directories" recipe ships skills with dangling template paths on other agents.
- Ecosystems shipped: `native`, `openspec` — `hooks/check-docs-updated.py:27-38`. OpenSpec hybrid mode: only `docs/decisions/` + linter + `scaffold/CLAUDE-openspec.md` block; never hand-edit `openspec/specs/` — `commands/sdd-init.md:41-58`, `skills/sdd-finalize/SKILL.md:20-23`.
- Spec Kit: mentioned as prior art and future adapter only ("ship when there is a user") — `README.md:149-150,186-187`, `docs/plans/archive/2026-07-19-openspec-ecosystem-adapters-design.md:121`. Kiro and BMAD: no occurrence in the repo (grep).
- Adapter model limits: an adapter is only `{detect, durable, ignore}` path prefixes in one Python dict inside the hook (`docs/decisions/0005-ecosystems-are-adapter-data.md:23-29`); adding one still requires editing skills, `/sdd-init`, and a scaffold rules block by hand (as was done for OpenSpec in commits `bc7fc3c`, `a62f0d2`, `72ad2c4`).

### Inferences
- ADR-0005's claim that a new ecosystem is "one dict entry + docs + tests - no architecture" understates the work: the OpenSpec adapter touched the hook, three skills, the init command, and a new scaffold file. Spec Kit (`specs/NNN-feature/` per-feature folders that are closer to plans than living specs, plus `.specify/memory/constitution.md`) does not map cleanly onto a single "durable prefix", so a Spec Kit adapter would need more than path data.
- For OpenSpec users the plugin's net addition is an ADR layer plus a reminder hook; the hook is satisfied only by `openspec/specs/` edits, which under OpenSpec happen at archive time, so mid-change turns will always trigger the reminder (false positives during normal propose/apply work).

### Gaps
- No verification that the skills load correctly in Codex, Cursor, or Gemini CLI; the repo contains no evidence anyone tried.

## 7. What is missing vs. a full SDD workflow?

### Takeaway
The plugin covers only the "where truth lives and how it retires" slice. Almost every upstream and downstream SDD stage (requirements elicitation, clarification, design, task breakdown, traceability, verification, drift detection) is absent by design or omission.

### Cited Findings
- Requirements authoring/clarification: no command or skill to create or refine a spec; `sdd-finalize` creates a spec from a template after the code exists — `skills/sdd-finalize/SKILL.md:17-20`. Template body is five headings with placeholders — `templates/spec.md:18-38`.
- Planning/task breakdown: no plan template, no tasks format, no command; `scaffold/docs/plans/` ships only a README and `.gitkeep` files; delegated to Superpowers — `docs/plans/README.md:3-5`.
- Spec-to-code traceability: no requirement IDs, no mapping from specs to code paths or tests; frontmatter has no `paths`/`covers` field — `skills/sdd-source-of-truth/SKILL.md:55-65`.
- Drift detection: none. The hook checks only "some durable file was touched this turn" (section 2); the linter does not read code (section 3). The authority rule says "spec wins" but nothing detects divergence.
- Spec validation/quality gates: no check for ambiguity, completeness, contradiction between specs, or history narration; linter is frontmatter-only.
- Acceptance criteria / test linkage: absent from templates and skills.
- Review/approval workflow: spec `status: draft|active` exists but no transition rule, reviewer, or PR integration; ADR `proposed|accepted` likewise.
- Monorepo/multi-repo: detection is `cwd/docs/specs` only (`hooks/check-docs-updated.py:185,165`); no nested-root discovery, no per-package config, no cross-repo references.
- i18n: plugin content is English-only (`docs/specs/001-plugin-architecture.md:111-113`); target-project docs are translated ad hoc by the model at init (`commands/sdd-init.md:62-64`), which also means the managed CLAUDE.md block is re-translated on each upgrade; frontmatter keys stay English.
- Versioning/release: version 0.2.0 in both manifests; no CHANGELOG, no git tags in this clone (`git tag` empty) although tags `v0.1.0`/`v0.2.0` are referenced (`docs/decisions/0001-repo-is-marketplace-and-plugin.md:27`, design plan), no release workflow. Per the docs, setting `version` "keeps users on that version until you change it" — [manifest reference](https://code.claude.com/docs/en/plugins-reference) — so fixes pushed without a bump do not reach users.
- Install/update story: install via two `/plugin` commands (`README.md:26-29`); upgrade of project files is "re-run /sdd-init to replace the marker block" (`commands/sdd-init.md:36-37`), which does not update the copied linter or READMEs; no uninstall guidance; no migration notes.
- Onboarding/docs: single README (209 lines) with a good conceptual pitch; no quickstart walkthrough, worked example of a full change, FAQ, troubleshooting (e.g., "hook not firing"), or contribution guide. The example spec/ADR pair exists in `scaffold/` but is deliberately not copied to projects (`commands/sdd-init.md:29-30`).
- Explicitly out of scope: RAG/Obsidian integration, PreToolUse hook on git commit, third-party marketplaces, non-Markdown formats — `docs/specs/001-plugin-architecture.md:122-127`; Spec Kit adapter, linting OpenSpec files, generating OpenSpec artifacts — `docs/plans/archive/2026-07-19-openspec-ecosystem-adapters-design.md:119-124`.
- No status/visibility command (list active specs, stale plans, unsuperseded contradictions), no metrics, no SessionStart hook to inject the spec index.

### Inferences
- Positioning relative to market tools: the plugin is complementary rather than competitive. It assumes another tool produces plans and code and focuses on post-hoc promotion and retirement. A comparison with Spec Kit/Kiro/BMAD on "workflow completeness" will be unfavorable; a comparison on "long-lived doc governance / anti-rot" is where it has something distinct.
- Cheap high-value additions implied by the gaps: a `paths:` frontmatter field enabling path-scoped hook matching (reduces both false positives and trivially-satisfied cases), linter rules for index sync and status enums, a shipped CI workflow/pre-commit snippet, and a spec-authoring command.

### Gaps
- No user feedback, issue tracker data, or adoption numbers are available in the repo to weigh which gaps matter most.

## 8. Concrete bugs, inconsistencies, stale docs, and risks

### Takeaway
Two defects are serious (non-executable launcher on POSIX; linter inline-comment parsing that breaks or bypasses the shipped templates); the rest are documentation inconsistencies and design risks.

### Cited Findings
- B1 (likely critical): `hooks/run-hook.cmd` is mode 100644 and registered as a directly executed shell-form command (`hooks/hooks.json:8`); `sh -c`/`bash -c` return exit 126 "Permission denied" [experiment]; Claude Code treats that as a non-blocking error ([hooks reference](https://code.claude.com/docs/en/hooks.md)). Test masks it (`tests/test_check_docs_updated.py:281-282`).
- B2 (high): linter does not strip inline comments (`scripts/check-docs.py:32-43`); `templates/adr.md:6` verbatim fails the linter; commented `status: active` evades the duplicate-active check [experiment].
- B3: linter docstring rule 5 (missing frontmatter) unimplemented (`scripts/check-docs.py:13` vs. `:51-53`); rule 3 is a warning, not a failure (`:11` vs. `:101-105`).
- B4: `/sdd-init` leaves example rows in the copied index READMEs (`scaffold/docs/specs/README.md:12`, `scaffold/docs/decisions/README.md:19-20` vs. `commands/sdd-init.md:29-30`).
- B5: install command mismatch: `README.md:28` says `/plugin install sdd-convention@sdd-convention`; `docs/specs/001-plugin-architecture.md:35-36` and `docs/decisions/0001-repo-is-marketplace-and-plugin.md:25-26` say `/plugin install sdd-convention`.
- B6: SPEC-001 item 3 lists skill triggers without `openspec/specs/` (`docs/specs/001-plugin-architecture.md:40-43`) while the skill description includes it (`skills/sdd-source-of-truth/SKILL.md:3`); the spec was bumped to v2 for adapters but this item was not updated.
- B7: SPEC-001 uses ad hoc numbering 12a-12d after 12 (`docs/specs/001-plugin-architecture.md:79-97`) and item 12c contains two paragraphs that partly restate each other (`:87-93`).
- B8: SPEC-001 item 17 says the README ships an AGENTS.md snippet "with the authority order, the four rules, and the finalize instruction" (`:117-119`); the README snippet contains only the finalize paragraph and points to `scaffold/CLAUDE.md` for the rest (`README.md:157-171`).
- B9: no git tags despite ADR-0001 and the plans referring to `v0.1.0`/`v0.2.0`; no CHANGELOG.
- B10: "hard enforcement lives in CI" (`hooks/check-docs-updated.py:14-15`) overstates what the linter does (section 1).
- B11: root `CLAUDE.md` triggers a `claude plugin validate` warning per the docs ([manifest reference](https://code.claude.com/docs/en/plugins-reference)); it is needed for dogfooding but ships to every installer of the plugin.
- B12: the repo ships 3,007 lines of archived plans and a 194-line Portuguese archived design to every installer; `docs/plans/archive/2026-07-19-sdd-convention-plugin.md` (1,917 lines) embeds older copies of the hook, linter, and skills, which is exactly the "stale A next to current B" content the convention warns about (mitigated only by the instruction to ignore archives).
- B13: maintainer's personal email is in both manifests (`.claude-plugin/plugin.json:7`, `.claude-plugin/marketplace.json:6,16`) — normal for plugins, noted as a privacy consideration only.
- B14: `python` vs. `python3` inconsistency between skill instructions and launcher (section 3).
- B15: the scaffold's archived example uses `superseded_by: SPEC-001@active` with a duplicate id and an extra `archived:` key not in the schema (`scaffold/docs/_archive/2026-01-example-payments-v1.md:2,7,9`).
- Risk: bus factor of one author, one day of commits (2026-07-19), no activity since; no issue templates or contribution docs.
- Risk: the hook's block reason and the CLAUDE.md block both say the agent may exit with one sentence; over time agents may learn to emit the sentence reflexively, and nothing measures how often that happens.

### Inferences
- B1 plus fail-open means a POSIX user could run the plugin for months believing the loop is closed while only the CLAUDE.md block and skills are doing anything. The file-mode pattern (everything 644, strong Windows focus in ADR-0003) suggests development on Windows, where the problem would not appear.

### Gaps
- B1 not reproduced inside an actual Claude Code session; severity is conditional on Claude Code not adjusting permissions or invoking through an interpreter.

## 9. Genuine differentiators and strengths

### Takeaway
The plugin's distinctive idea is lifecycle governance for agent-readable docs (one living spec per domain, contradictions only in a supersede-chained ADR log, plans disposable, archives invisible), delivered with very low footprint and an ecosystem-neutral ADR layer. Execution is strongest in the hook's defensive engineering and the retrofit playbook.

### Cited Findings
- Clear problem statement: contradictory old/new specs degrade agent reasoning; fix is "lifecycle governance, not retrieval" — `README.md:6-11`; RAG positioned as an index over `status: active` + `canonical: true` only — `README.md:173-179`.
- Mutability-based three-layer model with an explicit authority order that places code between spec and ADRs — `skills/sdd-source-of-truth/SKILL.md:12-16,40-49`.
- Supersede discipline with machine-readable frontmatter (`supersedes`/`superseded_by`, `status`) and a linter that checks the ADR chain — `templates/adr.md:2-8`, `scripts/check-docs.py:88-105`.
- Anti-rot rules that other tools rarely state: never fork `v2` files, never narrate history in specs, never infer state from plans, retire-never-delete with dated archive filenames — `skills/sdd-source-of-truth/SKILL.md:83-94,100-101`, `docs/_archive/README.md:9-13`.
- Brownfield support: an interactive, approval-gated, one-domain-at-a-time retrofit with context-economy rules and Canonical/Historical/Dead triage — `skills/sdd-retrofit/SKILL.md:22-66`.
- Deterministic end-of-turn nudge with an honest escape hatch ("Do not fabricate doc updates") — `hooks/check-docs-updated.py:40-47`; opt-in per project so a global install does not affect other repos — `README.md:36-38`.
- Defensive hook engineering: total fail-open, anti-loop, tolerant JSONL parsing, Windows/POSIX polyglot launcher, 31 tests on two OSes — `hooks/check-docs-updated.py:209-213`, `.github/workflows/ci.yml:13`.
- Zero runtime dependencies (Python stdlib only) — `docs/decisions/0004-python-stdlib-only.md:19-23`.
- Coexistence rather than replacement: OpenSpec hybrid mode refuses to create a second canonical tree and adds the ADR layer OpenSpec lacks; Superpowers is treated as the working layer — `commands/sdd-init.md:43-45`, `README.md:130-135,192-194`.
- Idempotent, marker-delimited managed block in CLAUDE.md/AGENTS.md as the upgrade channel — `commands/sdd-init.md:31-39`.
- Small prompt footprint: about 1,600 words across three skills plus a 54-line always-loaded block.
- The repo applies its own convention (SPEC-001 v2, ADR-0001..0005, archived plans/design), giving a real worked example — `docs/specs/001-plugin-architecture.md`, `docs/decisions/README.md:17-23`.

### Inferences
- The defensible niche versus Spec Kit / OpenSpec / Kiro / BMAD is "what happens to specs after the feature ships": consolidation into one living spec per domain, explicit supersession, and archive invisibility. Market tools mostly optimize the path from idea to tasks; this plugin optimizes long-term truth maintenance and could be positioned as an add-on layer to any of them (as already done for OpenSpec).
- The strengths are mostly conceptual and prompt-level; the mechanical enforcement that would make them reliable (working hook on all OSes, path-aware matching, stronger linter, CI wiring) is the main area to invest in.

### Gaps
- No evidence (evals, case studies, metrics) that the convention measurably reduces stale-doc errors in agent sessions; the benefit is argued, not demonstrated.
