# SDD tools landscape for AI coding agents (as of 2026-11-12)

Method notes for the report writer:
- GitHub release pages show day and month without a year. Where I write "(2026, year inferred)" the year is inferred from ordering and from independently dated sources, not printed on the page.
- Fetched pages were summarized by a small model; version numbers and command names are as reported by those summaries. Star counts differ a lot between sources and dates, so each is dated.
- The GitHub API was not available for these repos (session is scoped to one repository), so releases were read from the public HTML pages.
- Nothing here needed a 2025-only source except where explicitly flagged "2025 source".

## 1. GitHub Spec Kit: version, commands, extensions, agents, 2026 changes, criticisms

### Takeaway
Spec Kit went from 0.8.x (May 2026) to 1.0 (Sept 2026) to 1.4.0 (10 Nov 2026) and has become a platform: extensions, presets, workflows, bundles, catalogs, plus a new `converge` step. It still writes one folder per feature and has no built-in merge into a living system spec; `converge` only appends tasks and is forbidden from editing `spec.md`/`plan.md`.

### Cited Findings
- Latest release is 1.4.0 on 10 Nov (2026, year inferred); recent cadence is a release every 1 to 4 days (1.2.2 on 19 Oct through 1.4.0 on 10 Nov). 1.4.0 added HTTPS-only catalog sources, reasoning-effort mapping for Copilot/Codex/Claude Code, and workflow custom pipe filters — [spec-kit releases](https://github.com/github/spec-kit/releases)
- 1.3.0 (3 Nov) was breaking: core `/speckit.taskstoissues` was removed in favour of the `github` extension; it also added a `process_registered_command` hook. 1.2.5 (28 Oct) published extension development/publishing guides and exposed installed workflows through MCP. 1.2.3 (22 Oct) added `.presetignore` and a `none` integration (shared scaffolding only) — [spec-kit releases](https://github.com/github/spec-kit/releases)
- Repo shows 149.5k stars and 13.4k forks (fetched 2026-11-12) — [github/spec-kit](https://github.com/github/spec-kit)
- Earlier data points: version 0.8.7 with 93,000+ stars and 30+ agents (article dated 2026-05-29) — [SoftwareSeni](https://www.softwareseni.com/the-30-plus-framework-landscape-navigating-spec-driven-development-options-in-2026); `specify-cli` 1.0.12 released 2026-09-25 — [developertoolkit.ai Spec Kit](https://developertoolkit.ai/en/ecosystem/frameworks/spec-kit/)
- README core commands today: `/speckit-constitution`, `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`, `/speckit-converge`. Bundled extensions add bug fixing (`/speckit-bug-assess`, `-bug-fix`, `-bug-test`) and idea assessment (`/speckit-assess-intake`, `-research`, `-define`, `-shape`, `-decide`). The stated loop is implement then converge, repeated until it reports "Converged" — [github/spec-kit](https://github.com/github/spec-kit)
- Clarify, analyze and checklist still exist as optional steps (as of 1.0.12, 2026-09-26): clarify writes answers back into `spec.md`; analyze is read-only and cross-checks spec/plan/tasks, treating constitution conflicts as CRITICAL; checklist tests whether requirements are complete and clear, not whether code works — [developertoolkit.ai Spec Kit](https://developertoolkit.ai/en/ecosystem/frameworks/spec-kit/)
- Customization layers: extensions (commands, quality gates, hooks before/after commands), presets (templates, terminology, org/regulatory standards), project-local overrides, workflows (prompts, commands, gates, shell steps) with overlays, bundles (curated setups per role/team), and public/private catalogs. The README warns catalog listings are not audits — [github/spec-kit](https://github.com/github/spec-kit)
- Layout (1.0.12): `.specify/memory/constitution.md`; `specs/<NNN>-<feature>/` with `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `tasks.md`, `checklists/`; skills installed at `.claude/skills/speckit-*/SKILL.md` (or `.agents/skills/`, `.cursor/skills/`); extensions write to `.specify/bugs/` and `.specify/assessments/` — [developertoolkit.ai Spec Kit](https://developertoolkit.ai/en/ecosystem/frameworks/spec-kit/)
- Converge compares code against spec, plan, tasks and constitution; it does not edit code, spec or plan. On gaps it appends a `## Phase N: Convergence` section to `tasks.md` (CRITICAL/HIGH first). The reviewer stresses it is a model judgment, not a test — [developertoolkit.ai Spec Kit](https://developertoolkit.ai/en/ecosystem/frameworks/spec-kit/)
- Official guidance on evolution (from search snippet of the official guide): when intended behaviour changes, revise the existing `spec.md` first, then regenerate plan and tasks. For existing projects, a new `spec.md` "defines the change you intend to make, not a retroactive specification of every existing behavior" — [evolving-specs guide](https://raw.githubusercontent.com/github/spec-kit/main/docs/guides/evolving-specs.md) (direct fetch returned 404 on 2026-11-12; content known only from the search snippet); [Adopting Spec Kit in an Existing Project](https://github.github.com/spec-kit/guides/existing-projects.html)
- Criticism, per-feature specs: "Spec Kit writes one folder per feature, so nothing merges `specs/001-audit-log-export/spec.md` into a current description of the whole system"; living spec and drift detection are left to the user (2026-09-26) — [developertoolkit.ai Spec Kit](https://developertoolkit.ai/en/ecosystem/frameworks/spec-kit/)
- Criticism, verbosity and governance: "a sea of markdown documents, long agent run-times and unexpected friction" (Scott Logic, quoted); no enforcement or verification; specs stop governing after first generation (article dated 2026-06-03) — [CodeMySpec best tools](https://codemyspec.com/blog/best-spec-driven-development-tools)
- Criticism, upgrades and health (2026-05-29, citing the RanTheBuilder benchmark): upgrades can overwrite customization files; benchmark score 2.77/5, lowest of four; 36.8% issue close rate; skews greenfield — [SoftwareSeni](https://www.softwareseni.com/the-30-plus-framework-landscape-navigating-spec-driven-development-options-in-2026)
- Thoughtworks Radar rated Spec Kit Assess (April 2026) and describes it as fitting greenfield better than brownfield — [Thoughtworks Radar: OpenSpec](https://www.thoughtworks.com/en-gb/radar/tools/openspec)
- Community extensions exist for drift: a third-party "Canon" extension lists spec-first, code-first and spec-drift workflows (search snippet only, not verified) — [zarndotuk/spec-kit](https://github.com/zarndotuk/spec-kit)

### Inferences
- The SoftwareSeni health number (37 commits in 90 days, May 2026) conflicts with the near-daily release cadence seen in Oct-Nov 2026; either activity rose sharply after 1.0 or the benchmark metric was measured differently. Treat the May number as stale.
- The README mentions a news item on "maintaining capability-level specs", which suggests GitHub is aware of the living-spec gap, but I found no built-in capability-spec format.
- Spec Kit's direction in H2 2026 is ecosystem and automation (workflows, catalogs, MCP exposure), not long-term spec maintenance. That leaves room for a convention-focused plugin.

### Gaps
- Could not read the official evolving-specs guide or the "capability-level specs" news item directly (404), so details of GitHub's own answer to the living-spec criticism are unconfirmed.
- Exact current list of supported agents not retrieved; only "30+ agents" (May 2026) is sourced.
- Release notes for 1.0.0 itself (what defined "1.0") not retrieved.

## 2. OpenSpec (Fission-AI): version, workflow, 2026 changes, layout, archive merge

### Takeaway
OpenSpec shipped v2.0.0 on 11 Nov 2026 (one day before this research): `/opsx:*` slash commands were removed and replaced with skills installed in a shared `.agents/skills/` folder. Its model is unchanged: persistent source-of-truth specs in `openspec/specs/`, change folders with delta specs, and an archive step that merges deltas into the specs. Thoughtworks moved it to Trial in November 2026.

### Cited Findings
- v2.0.0 on 11 Nov (2026, year inferred): skills now install in a shared `.agents/skills/` folder that tools such as Claude Code and Kiro link to; `/opsx:*` slash commands removed, each with a skill replacement; Amazon Q Developer support dropped — [OpenSpec releases](https://github.com/Fission-AI/OpenSpec/releases)
- v1.17.0 (9 Nov): `openspec update` upgrades from any release since 0.12 in one run. v1.16.1 (7 Nov): stricter parsing; delta specs under unrecognized sections now fail validation and archiving. v1.16.0 (30 Oct): Node.js 22.12+ required for npm installs; `validate` warns when a scenario lacks WHEN/GIVEN or THEN. v1.15.0 (24 Oct): standalone binary without Node.js; `openspec update --dry-run`. v1.14.2 (15 Oct): warnings when archive would drop content from delta specs. v1.14.0 (30 Sep): ten new tools (Amp, Grok Build, Warp among them), `openspec list --archived`. v1.13.2 (23 Sep): `/opsx:verify` reports what it actually checked — [OpenSpec releases](https://github.com/Fission-AI/OpenSpec/releases)
- Repo shows 74.7k stars, 5.1k forks, "30+ tools" supported (fetched 2026-11-12) — [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)
- Current commands (skills). Default profile: `/openspec-explore`, `/openspec-propose <name>`, `/openspec-apply-change`, `/openspec-archive-change`. Expanded profile (via `openspec config profile` then `openspec update`): `openspec-new-change`, `openspec-continue-change`, `openspec-ff-change`, `openspec-verify-change`, `openspec-bulk-archive-change`, `openspec-onboard`. Codex uses a `$` prefix — [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)
- Layout: `openspec/specs/` (source of truth); `openspec/changes/<change-name>/` with `proposal.md`, `specs/` (deltas), `design.md`, `tasks.md`; `openspec/changes/archive/<date>-<change-name>/` — [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)
- Archive mechanics: ADDED requirements are appended to the main spec; MODIFIED replace the existing requirement; REMOVED are deleted. If removal empties a capability, the spec file is deleted only when the change sets `retire_capabilities: true`. A `## Purpose` in a delta seeds a new spec and is ignored for an existing one. The change folder moves to `changes/archive/` with a date prefix and all artifacts are kept — [OpenSpec concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md)
- Artifact graph: `schema.yaml` defines each artifact, its file and what it requires. In the built-in `spec-driven` schema, specs and design require proposal, and tasks require specs and design. Dependencies enable, they do not force order. Custom schemas via `openspec schema init` / `openspec schema fork`; there is a community schema catalog — [OpenSpec concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md); [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)
- Decisions: no ADR concept. `design.md` holds "Decision:" entries; history lives only in archived change folders — [OpenSpec concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md)
- Limits noted by a reviewer (2026-06-03): `verify` does not block; `validate` checks structure, not behaviour; drift is handled manually; quoted user complaint that specs "keep drifting and drifting until you have duplication and contradictions" — [CodeMySpec best tools](https://codemyspec.com/blog/best-spec-driven-development-tools)
- Thoughtworks Radar Vol. 35 (Nov 2026): Trial, up from Assess (Apr 2026). Praised for brownfield and for a spec-anchored workflow of deltas against a persistent spec. Caution: agents generate Markdown prolifically, and maintaining the persistent spec takes discipline even with archiving — [Thoughtworks Radar: OpenSpec](https://www.thoughtworks.com/en-gb/radar/tools/openspec)
- Benchmark (cited 2026-05-29): highest overall score 4.00/5, about $95 per feature; criticism of single-maintainer bus factor and 24.2% issue close rate — [SoftwareSeni](https://www.softwareseni.com/the-30-plus-framework-landscape-navigating-spec-driven-development-options-in-2026)
- Star trajectory: 52,100 stars reported as of June 2026 (search snippet) — [developertoolkit.ai frameworks compared](https://developertoolkit.ai/en/ecosystem/frameworks/spec-driven-frameworks/)

### Inferences
- The v2.0.0 change directly affects any OpenSpec adapter: anything keyed on `/opsx:*` command names or on per-tool command files is now stale; detection should rely on the `openspec/` directory layout and skill names instead.
- OpenSpec's own releases (v1.14.2, v1.16.1) show archive-time content loss was a real problem, which is why they added warnings and stricter parsing. Archive-merge is not a solved operation.
- OpenSpec has no status frontmatter, no supersedes chain and no ADRs. The "why" is recoverable only by reading archived change folders. This is the clearest complement a convention plugin can offer.

### Gaps
- RENAMED deltas are not described on the concepts page; handling unconfirmed.
- `openspec validate --strict` behaviour not confirmed from primary docs.
- Full v2.0.0 migration notes not read.

## 3. AWS Kiro: specs, steering, hooks, 2026 updates

### Takeaway
Kiro is now a family (IDE 1.4.x, CLI 3.x, Web, open-source Kiro Crew) with three spec types (Feature requirements-first or design-first, Bugfix, Quick Spec), requirements analysis, and property-based "correctness" testing. I found no documented mechanism for syncing specs after implementation or detecting drift.

### Cited Findings
- Spec types (docs page updated 2026-10-15): Feature Specs (Requirements-First or Design-First), Bugfix Specs (`bugfix.md` instead of `requirements.md`), and Quick Spec (all three files in one pass, no approval gates). Files: `requirements.md`/`bugfix.md`, `design.md`, `tasks.md`. "Analyze Requirements" checks for inconsistencies, ambiguities and gaps (IDE and CLI). Running all tasks builds a dependency graph and runs independent tasks concurrently in waves — [Kiro specs docs](https://kiro.dev/docs/specs/)
- Correctness: Kiro integrates property-based testing through the spec workflow, generating many random inputs to try to violate properties derived from requirements; listed as IDE only (docs dated 2026-08-04 and 2026-10-15) — [Kiro correctness docs](https://kiro.dev/docs/specs/correctness/); [Kiro specs docs](https://kiro.dev/docs/specs/)
- Specs live in `.kiro/specs/<feature>/`, shared between IDE and CLI, with human approval gates between phases (secondary source, 2026-09-26) — [developertoolkit.ai Kiro](https://developertoolkit.ai/en/comparison/kiro/)
- November 2026 changelog: CLI 3.2.1 (11 Nov), CLI 3.2.0 and IDE 1.4.154 (10 Nov, permission modes, spec task fixes), IDE 1.4.121 and CLI 3.1.0 (5 Nov, Pre/Post Compaction hooks), Enterprise Management preview (10 Nov, one policy across clients covering steering files, Skills and Powers), Kiro Crew 0.12.0 (5 Nov) — [Kiro changelog](https://kiro.dev/changelog/)
- Other 2026 features listed in Kiro's README (2026-09-26): steering, hooks, Powers (on-demand tools and knowledge), MCP, custom agents, checkpoints with rewind, cloud sessions (preview). Kiro Crew is Apache-2.0, created 2026-07-16, with Claude Code/Codex backends from 0.6.0 and OpenCode from 0.7.0 (Preview). Kiro's own product source is closed — [developertoolkit.ai Kiro](https://developertoolkit.ai/en/comparison/kiro/)
- Pricing (checked 2026-10-12): Free 50 credits, Pro $20, Pro+ $40, Pro Max $100, Power $200 — [developertoolkit.ai Kiro](https://developertoolkit.ai/en/comparison/kiro/)
- Requirement-to-task traceability is reported as part of the generated task list; tests run via Agent Hooks; pricing backlash on Hacker News (2026-06-03) — [CodeMySpec best tools](https://codemyspec.com/blog/best-spec-driven-development-tools)
- Criticism: designed for greenfield; Design-first and Bugfix workflows were added in response (2026-05-29) — [SoftwareSeni](https://www.softwareseni.com/the-30-plus-framework-landscape-navigating-spec-driven-development-options-in-2026)
- GA plus CLI and spec correctness were announced together in the GA release — [Kiro GA blog](https://kiro.dev/blog/general-availability/); [Kiro changelog: spec correctness and CLI](https://kiro.dev/changelog/spec-correctness-and-cli/) (search snippets; date of GA not confirmed here, likely late 2025)

### Inferences
- Kiro is the only mainstream tool tying requirements to executable properties, which is the strongest requirement-to-test traceability on offer; it is IDE-only and proprietary.
- Kiro specs remain per-feature folders, like Spec Kit; steering files are the persistent layer. No system-level living spec was found.

### Gaps
- Only page 1 of 19 changelog pages was read; earlier 2026 spec-specific features (if any) on spec sync or drift are unverified. Absence of drift tooling is "not found", not "confirmed absent".
- CLI version numbers conflict across sources: CLI 2.29.0 on 2026-10-09 ([developertoolkit.ai](https://developertoolkit.ai/en/comparison/kiro/)) versus CLI 3.1.0 on 5 Nov ([Kiro changelog](https://kiro.dev/changelog/)). Plausibly a major bump in between; not confirmed.

## 4. Other tools: BMAD, Tessl, Agent OS, cc-sdd, GSD, Superpowers, Taskmaster, spec-workflow MCP, native plan modes

### Takeaway
The field split in 2026: heavy frameworks slimmed down (BMAD cut core skills from 14 to 8; Agent OS v3 dropped spec writing and implementation in favour of Claude Code plan mode), Tessl pivoted its shipped product from a spec registry to a skills registry, and nearly everything is now distributed as agent skills. Native plan modes produce disposable plans with no lifecycle.

### Cited Findings
BMAD-METHOD
- Latest v6.12.4 on 14 Oct (2026, year inferred); v7 is in preview. v6.12.0 (4 Sep): Build assesses how much ceremony a change needs; review triage logs a verdict and evidence per finding. v6.11.0 (10 Aug): Quick Dev renamed Build; core drops from 14 skills to 8; `bmad-project-context` writes one verified block to `AGENTS.md`. v6.10.0 (3 Jul): opt-in `bmad-loop` for unattended dev loops. v6.9.0 (22 Jun): `bmad-architecture` rewritten around a lean spine; shared memlog replaces per-skill decision logs. v6.8.0 (25 May): `bmad-spec` distills input into a compact `SPEC.md` — [BMAD releases](https://github.com/bmad-code-org/BMAD-METHOD/releases)
- 46,700+ stars at v6.6.0 (2026-04-29); artifacts (PRD, architecture, stories) in `docs/`; adversarial review and Party Mode; about $200 per feature in full mode; 94.3% issue close rate — [SoftwareSeni](https://www.softwareseni.com/the-30-plus-framework-landscape-navigating-spec-driven-development-options-in-2026)
- Criticism: about two months to learn; high token cost; weak on legacy monoliths (2026-06-03) — [CodeMySpec best tools](https://codemyspec.com/blog/best-spec-driven-development-tools)

Tessl
- Spec Registry open beta 2025-09-16 with 10,000+ library specs (2025 source); repositioned around skills on 2026-01-29 (skills registry, `tessl install`); Snyk security scores on public skills from March 2026; 3,000+ skills and Framework still closed beta as of June 2026 (search snippets) — [Tessl launch blog](https://tessl.io/blog/tessl-launches-spec-driven-framework-and-registry/); [CodeMySpec Tessl review](https://codemyspec.com/blog/tessl-review)
- Spec-as-source regeneration engine in closed beta about nine months, JavaScript-only; Birgitta Böckeler observed non-deterministic output from identical specs; shipped product is the skills registry (2026-06-03) — [CodeMySpec best tools](https://codemyspec.com/blog/best-spec-driven-development-tools)

Agent OS (Builder Methods)
- v3.0 released January 2026 (tag 20 Jan). Spec writing moved to Claude Code plan mode, enhanced by `/shape-spec`; implementation and orchestration phases retired; no subagents installed; new `/discover-standards` and `/inject-standards` — [Agent OS migration guide](https://buildermethods.com/agent-os/migration); [Agent OS v3 discussion](https://github.com/buildermethods/agent-os/discussions/310)
- Standards are advisory, with no gating and no verification loop (2026-06-03) — [CodeMySpec best tools](https://codemyspec.com/blog/best-spec-driven-development-tools)

cc-sdd (gotalab)
- About 3.8k stars; v3.0 line (3.1.0 seen 2026-09-26); 17 skills including `kiro-discovery`, `kiro-spec-init`, `kiro-spec-requirements`, `kiro-spec-design`, `kiro-spec-tasks`, `kiro-impl`, `kiro-spec-batch` (cross-spec review for contradictions), `kiro-steering`, `kiro-validate-gap` (brownfield gap check before design). Kiro-compatible `.kiro/` layout. States "Code remains the source of truth"; learnings carried in `## Implementation Notes` in `tasks.md`. Stable on Claude Code and Codex; beta on Cursor, Copilot, Devin, OpenCode, Gemini CLI, Antigravity — [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd); [developertoolkit.ai Kiro](https://developertoolkit.ai/en/comparison/kiro/)

GSD (get-shit-done)
- 61,000+ stars in under five months since December 2025; researchers, planners, executors and verifiers each in a fresh context; 14 runtimes; no published benchmark (2026-05-29) — [SoftwareSeni](https://www.softwareseni.com/the-30-plus-framework-landscape-navigating-spec-driven-development-options-in-2026)
- 48.4K stars reported 2026-04-07; in May 2026 maintainers migrated active development to `open-gsd/get-shit-done-redux` citing trust and ownership concerns about the former upstream (search snippets) — [Augment: GSD](https://www.augmentcode.com/learn/gsd-stars-spec-driven-dev-claude-code); [GitHub topic get-shit-done](https://github.com/topics/get-shit-done)

Superpowers (obra)
- v7.0.2 on 3 Nov (2026, year inferred). v7.0.0 (10 Oct) rebuilt brainstorming and added an Antigravity manifest. v6.4.2 (25 Sep): `writing-plans` produces leaner plans that record decisions instead of full code. v6.3.0 (12 Aug): plans carry a `Spec:` pointer; ceremony scales with task size. v6.2.0 (24 Jul): plan-scoped SDD workspace `.superpowers/sdd/<plan-basename>/`, deleted after a clean final review; review-fix loop with five-round circuit breaker. v6.1.0 (30 Jun): Gemini CLI support removed after Google EOLed it — [superpowers releases](https://github.com/obra/superpowers/releases)

Taskmaster
- MCP-based task breakdown for Cursor, Windsurf, Roo and others; 36 tools in its MCP server; no reliable 2026 release notes found (search snippets) — [HackerNoon Taskmaster](https://hackernoon.com/developers-embrace-taskmaster-an-ai-scrum-master-for-code)

Native plan modes
- GitHub Copilot plan mode makes no code changes until the plan is approved, and can open the plan as Markdown; public preview in JetBrains, Eclipse and Xcode on 2025-11-18 (2025 source) — [GitHub changelog](https://github.blog/changelog/2025-11-18-plan-mode-in-github-copilot-now-in-public-preview-in-jetbrains-eclipse-and-xcode/); [Copilot plan mode docs](https://docs.github.com/en/copilot/how-tos/copilot-in-your-ide/use-copilot-agents/use-plan-mode)
- Cursor Plan Mode: plan, clarifying questions, affected files, review before coding; "no spec lifecycle, no drift detection, no living-spec sync" (2026-05-29) — [SoftwareSeni](https://www.softwareseni.com/the-30-plus-framework-landscape-navigating-spec-driven-development-options-in-2026)
- JetBrains Junie reached GA on 2026-06-17 (search snippet from a secondary blog) — [tech-insider Junie comparison](https://tech-insider.org/jetbrains-junie-vs-github-copilot-vs-cursor-2026/)

Newcomers
- CodeMySpec (Claude Code plugin plus local MCP server; requirement graph; BDD scenarios as a mandatory gate; QA subagent drives a real browser; Phoenix/Elixir only, early access; note the source is the vendor's own blog) — [CodeMySpec best tools](https://codemyspec.com/blog/best-spec-driven-development-tools)
- `cc-spex` ships an "evolve" skill for spec evolution and reconciliation (search snippet only) — [skills.sh cc-spex evolve](https://skills.sh/rhuss/cc-spex/evolve)
- Brief (briefhq.ai) argues decisions change outside the repo, so specs go stale unless a separate decision record is kept current (vendor pitch) — [Brief blog](https://briefhq.ai/blog/why-spec-driven-development-isnt-enough/)

### Inferences
- Superpowers (v6.4.2 plans "record decisions"; workspace deleted after review) and Agent OS v3 both treat plans as disposable, matching the sdd-convention position that plans are ephemeral. Neither then promotes what survives into a durable spec or ADR.
- cc-sdd explicitly takes the opposite authority order to sdd-convention ("code remains the source of truth" versus "the spec wins").
- GSD's fork in May 2026 and OpenSpec's single-maintainer note show governance risk is a live adoption concern for community tools.

### Gaps
- spec-workflow MCP: no 2026 information found.
- Taskmaster: current version and status unconfirmed.
- Google Antigravity/Jules and JetBrains Junie plan artifact formats: no primary source found.
- Superpowers and cc-sdd star counts for Superpowers not retrieved; where Superpowers brainstorming saves design docs is not stated on the releases page.
- Amazon Q Developer: only indirect signals (described as succeeded by Kiro; OpenSpec dropped support in v2.0.0).

## 5. Cross-tool comparison: artifacts, lifecycle, drift, validation, traceability, multi-agent, adoption

### Takeaway
Only OpenSpec has a built-in path from change to persistent spec (archive-merge). Spec Kit, Kiro and cc-sdd keep per-feature folders; BMAD keeps PRD/architecture/stories; Superpowers and plan modes discard. Validation is almost everywhere structural or model-judged, not behavioural.

### Cited Findings
| Tool | Durable artifacts and location | Who updates spec after implementation | Drift / staleness | Validation | Traceability | Adoption (dated) |
|---|---|---|---|---|---|---|
| Spec Kit | `specs/<NNN>-<feature>/*`, `.specify/memory/constitution.md` | User revises `spec.md` first, then regenerates; converge may not edit spec | `converge` appends tasks; model judgment | `analyze` (read-only), `checklist`, extension quality gates | spec to plan to tasks within one feature folder | 149.5k stars, 1.4.0 (Nov 2026) |
| OpenSpec | `openspec/specs/`, `openspec/changes/`, `changes/archive/` | Archive step merges deltas | `verify` skill, non-blocking; manual otherwise | `openspec validate` (structure; scenario step warnings) | proposal to delta spec to tasks per change; history in archive | 74.7k stars, v2.0.0 (Nov 2026), Radar Trial |
| Kiro | `.kiro/specs/<feature>/`, steering files | Not documented | Not found | Analyze Requirements; property-based tests | requirements (EARS) to tasks to properties | closed source; CLI 3.2.1 (Nov 2026) |
| BMAD | PRD, architecture, stories in `docs/`; `AGENTS.md` block | Agents per workflow | Not found | adversarial review with logged verdicts | PRD to epics to stories | v6.12.4 (Oct 2026), 46.7k stars (Apr 2026) |
| cc-sdd | `.kiro/` specs and steering | Code is source of truth; notes in `tasks.md` | `kiro-validate-gap`, `kiro-spec-batch` | gap and cross-spec review | requirements to design to tasks | ~3.8k stars, v3.x |
| Agent OS v3 | standards, product docs | Not applicable (specs via plan mode) | None | None (advisory) | None | v3.0 (Jan 2026) |
| Superpowers | plan with `Spec:` pointer; workspace deleted | Not applicable | None | review-fix loop | spec pointer in plan | v7.0.2 (Nov 2026) |
| Plan modes | transient plan | Nobody | None | None | None | built in |

Sources for the table: [github/spec-kit](https://github.com/github/spec-kit); [developertoolkit.ai Spec Kit](https://developertoolkit.ai/en/ecosystem/frameworks/spec-kit/); [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec); [OpenSpec concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md); [OpenSpec releases](https://github.com/Fission-AI/OpenSpec/releases); [Kiro specs docs](https://kiro.dev/docs/specs/); [Kiro changelog](https://kiro.dev/changelog/); [BMAD releases](https://github.com/bmad-code-org/BMAD-METHOD/releases); [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd); [Agent OS migration guide](https://buildermethods.com/agent-os/migration); [superpowers releases](https://github.com/obra/superpowers/releases); [SoftwareSeni](https://www.softwareseni.com/the-30-plus-framework-landscape-navigating-spec-driven-development-options-in-2026); [CodeMySpec best tools](https://codemyspec.com/blog/best-spec-driven-development-tools)

- A controlled benchmark by Uvik ran these tools on the same 50 production Python tickets with a no-spec control (results not retrieved) — [Uvik benchmark](https://uvik.net/blog/spec-driven-development-benchmark/)
- A community repo compares spec frameworks side by side (not read) — [cameronsjo/spec-compare](https://github.com/cameronsjo/spec-compare)

### Inferences
- No tool surveyed uses status frontmatter (`active`/`superseded`/`archived`) on specs, nor a supersedes chain for decisions. OpenSpec deletes or replaces requirement text in place; the prior version survives only in the archived change folder.
- No tool surveyed ships a deterministic staleness check (for example, code changed but spec `updated` date did not). All drift checks found are LLM judgments.

### Gaps
- Kiro and BMAD cells marked "Not found" reflect limited reading (one docs page, release notes), not a confirmed absence.
- Test-to-requirement traceability beyond Kiro's properties and CodeMySpec's BDD gate was not found for any tool.

## 6. Table stakes in 2026, and what nobody does well

### Takeaway
Table stakes: repo-resident Markdown specs, agent-agnostic installs delivered as skills, a clarify/analyze step before coding, ceremony that scales with task size, and brownfield entry points. Unsolved: enforcement and verification, long-term maintenance of a system-level living spec, decision history, and deterministic drift detection.

### Cited Findings
- Stated table stakes: repo-resident specs, bring-your-own-agent, no token markup, specs before code; portability "is table stakes, not a moat" (2026-06-03) — [CodeMySpec best tools](https://codemyspec.com/blog/best-spec-driven-development-tools)
- Stated unsolved problem: enforcement and verification; most tools score "none" on both; "a spec nothing enforces is documentation that drifts" (2026-06-03, vendor blog) — [CodeMySpec best tools](https://codemyspec.com/blog/best-spec-driven-development-tools)
- Skills as the delivery format: OpenSpec v2.0.0 replaced commands with skills in `.agents/skills/`; Spec Kit installs `speckit-*` skills; BMAD and cc-sdd are skill-based; Tessl pivoted to a skills registry — [OpenSpec releases](https://github.com/Fission-AI/OpenSpec/releases); [developertoolkit.ai Spec Kit](https://developertoolkit.ai/en/ecosystem/frameworks/spec-kit/); [BMAD releases](https://github.com/bmad-code-org/BMAD-METHOD/releases); [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd); [CodeMySpec Tessl review](https://codemyspec.com/blog/tessl-review)
- Ceremony scaling: BMAD Build assesses ceremony per change (v6.12.0); Superpowers scales brainstorming to task size (v6.3.0); Kiro Quick Spec skips gates — [BMAD releases](https://github.com/bmad-code-org/BMAD-METHOD/releases); [superpowers releases](https://github.com/obra/superpowers/releases); [Kiro specs docs](https://kiro.dev/docs/specs/)
- Bugfix and brownfield paths are now standard: Kiro Bugfix Specs, Spec Kit `bug` extension, cc-sdd `kiro-validate-gap`, OpenSpec `onboard` — [Kiro specs docs](https://kiro.dev/docs/specs/); [github/spec-kit](https://github.com/github/spec-kit); [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd); [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)
- Drift is the dominant reported failure: practitioners describe specs drifting "within days, not months" and call static specs going out of sync the main failure mode (search snippets) — [dev.to critique](https://dev.to/sam_curatedmcp/spec-driven-development-renamed-an-old-problem-it-didnt-solve-it-tags-ai-productivity-347a); [agentpatterns.ai](https://agentpatterns.ai/workflows/spec-driven-development/)
- Thoughtworks: SDD technique was Assess in Nov 2025; the April 2026 OpenSpec blurb advises teams to revisit whether SDD tooling is still needed as native agent capabilities improve; the Nov 2026 blurb warns about Markdown sprawl and the discipline needed for the persistent spec — [Thoughtworks Radar: OpenSpec](https://www.thoughtworks.com/en-gb/radar/tools/openspec)
- Böckeler (Thoughtworks podcast): the term is fuzzy and people self-identify into SDD; secondary commentary reports Beck and Fowler criticized writing the whole spec before implementation in January 2026, and argues "spec-anchored" (spec persists but is not frozen) is the answer (search snippets; Fowler's original not read) — [Thoughtworks podcast](https://www.thoughtworks.com/insights/podcasts/technology-podcasts/what-is-spec-driven-development); [Level Up Coding](https://levelup.gitconnected.com/sdd-kent-beck-and-martin-fowler-why-spec-anchored-development-wins-a4c838d5be11); [DZone](https://dzone.com/articles/spec-driven-development)
- A 2026 article frames drift around who decides the sync direction and proposes a "divergence register" (title only; paywalled) — [Level Up Coding: spec and code drift](https://levelup.gitconnected.com/spec-and-code-drift-who-decides-the-sync-direction-the-masking-diff-and-the-divergence-register-dd1d0de74f0b)

### Inferences
Possible gaps and opportunities for sdd-convention, derived from the above (these are my reading, not sourced claims):
- Strengths that are rare elsewhere: status frontmatter on specs, ADR supersedes chain, explicit authority order, retire-never-delete. No surveyed tool has these.
- OpenSpec adapter needs review against v2.0.0 (skills in `.agents/skills/`, `/opsx:*` gone, `retire_capabilities` deletes spec files, which conflicts with "retire, never delete").
- A Spec Kit adapter is the obvious missing piece: 149.5k stars and a documented lack of merge from `specs/<NNN>-feature/` into a system spec. A "promote feature spec into `docs/specs`" step would fill a publicly criticized hole. Spec Kit's extension/preset system is a natural distribution channel.
- A Kiro/cc-sdd adapter (`.kiro/specs`, steering) would cover the third common layout.
- Deterministic drift signals are absent market-wide: the linter could flag code paths changed since a spec's `updated` date, or specs untouched for N commits in their area. The current Stop hook is a reminder; competitors use model-judged verify/converge steps, so a `verify`-style skill would bring parity while the deterministic check would differentiate.
- Requirement IDs and traceability (requirement to test) are where Kiro and CodeMySpec lead; a light convention for requirement IDs referenced from tests would close part of that gap without heavy tooling.
- Scenario format lint (OpenSpec warns on scenarios lacking WHEN/THEN) is a cheap linter parity item.
- Ceremony scaling and a bugfix path are table stakes; a convention should say when a change needs no spec or ADR update.
- Delivery as skills in the shared `.agents/skills/` location is becoming the cross-agent norm; a Claude-Code-only plugin limits reach.
- The "divergence register" idea (recording known spec/code divergences and the chosen sync direction) maps well onto the existing rule that reconciliation is recorded in an ADR.

### Gaps
- Martin Fowler's and Kent Beck's original January 2026 texts were not read; their positions are reported second-hand.
- No independent, quantitative study of spec staleness over time was found.
- Hacker News discussions were not searched directly.
- The Level Up Coding "frameworks a year later" article (pattern families and measurements) returned HTTP 403 and could not be read.
