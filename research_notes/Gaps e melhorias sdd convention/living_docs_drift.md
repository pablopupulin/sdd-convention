# Living docs, ADRs and spec-vs-code drift for AI coding agents (state as of 2026-11-12)

Reading notes for the writer:
- Every finding carries the date of the source. "[2025 only]" marks claims I could confirm only from 2025 (or older) material.
- "[snippet]" marks claims taken from a search-result summary where I did not open the page itself. Treat these as leads, not verified facts.
- Most tool/vendor pages are self-descriptions, not independent evaluations. The only peer-style empirical evidence found is the ETH Zurich AGENTS.md paper.

## 1. Critiques and empirical evidence on SDD, context files and documentation rot

### Takeaway
The strongest 2026 evidence says always-loaded context files cost tokens (+20% or more) without reliably improving task success, and Thoughtworks' November 2026 Radar now lists "agent instruction bloat" and "AI-driven documentation sprawl" as Caution items. The consistent recommendation is a lean always-on file, progressive disclosure of everything else, and conversion of rules into deterministic checks. This supports the plugin's "pointer, not content" CLAUDE.md block, but challenges any growth of that block and any convention that multiplies markdown.

### Cited Findings
- Gloaguen, Mündler-Sasahara, Müller, Raychev, Vechev, "Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?" (arXiv 2602.11988; v1 12 Feb 2026, v2 23 Jun 2026, v3 29 Sep 2026): context files "do not generally improve task success rates" and increase inference cost by over 20% on average, across LLMs, agents, and both LLM-generated and developer-committed files. — [arXiv abstract](https://arxiv.org/abs/2602.11988)
- Same paper: agents do follow the instructions in context files; repository overviews (commonly recommended by model providers) were not helpful; authors recommend using context files mainly for non-standard practices and evaluating any change before deploying it. — [arXiv abstract](https://arxiv.org/abs/2602.11988)
- Same paper, v1 details [snippet, v1 HTML not opened by me]: developer-written files gave about +4% average improvement, LLM-generated files a small negative effect; when README/docs were removed, LLM-generated context files did help (interpreted as redundancy with existing docs); context files induce more exploration and testing but do not reduce steps to reach relevant files; evaluated Claude Code, Codex and Qwen Code on SWE-bench Lite plus a new "AGENTbench"; Python only. — [arXiv v1 HTML](https://arxiv.org/html/2602.11988v1). Note the abstract wording changed between versions ("tend to reduce success" in v1 snippet vs "do not generally improve" in v3), so quote v3.
- The paper is listed in the ICLR 2026 virtual site [snippet]. — [ICLR listing](https://iclr.cc/virtual/2026/10021235)
- Thoughtworks Technology Radar Vol. 35 (November 2026), Techniques: "Progressive context disclosure" is in Adopt (keep AGENTS.md lean, load other context on demand); "Agent instruction bloat" is Caution (instructions grow, become contradictory and stale; convert rules into hooks and prune with each new model); "AI-driven documentation sprawl" is Caution; "Naive context compression" is Caution; "Context profiling" (measure where tokens go) is Assess; "Harness quality evaluation" is Assess (guardrails only help if they actually work; test them). — [Thoughtworks Radar Techniques](https://www.thoughtworks.com/en-sg/radar/techniques)
- Radar blip "AI-driven documentation sprawl" (Caution, published 4 Nov 2026): agents and SDD tools produce polished-looking markdown that gives a false impression of quality; docs are usually not covered by automated gates; repositories become a "big ball of documentation mud" of verbose, outdated, contradictory specs; obsolete decision records and conflicting specs consume agent context and feed it unreliable information. Mitigation offered: treat markdown as a first-class artifact and spend human effort pruning and consolidating so context stays "crisp, relevant and authoritative". — [Thoughtworks blip](https://www.thoughtworks.com/radar/techniques/ai-driven-documentation-sprawl)
- Radar blip "Agent instruction bloat": models attend less to content buried in long contexts, so important rules get ignored as instructions grow; November 2026 revision advises converting instructions into deterministic hooks/checks and re-testing rules against new models; cites an Anthropic claim of removing over 80% of Claude Code's system prompt for its latest models with no measurable loss [snippet, figure not independently verified]. — [Thoughtworks blip](https://www.thoughtworks.com/radar/techniques/agent-instruction-bloat)
- Same Radar page lists as related, with their last-assessed dates: Context engineering Adopt (Apr 2026), Curated shared instructions for software teams Adopt (Apr 2026), Spec-driven development Assess (Nov 2025), AGENTS.md Trial (Nov 2025), Feedback sensors for coding agents Trial (Apr 2026), Agent skills Trial (Apr 2026), Lightweight ADRs Adopt (May 2018). — [Thoughtworks Radar Techniques](https://www.thoughtworks.com/en-sg/radar/techniques)
- Radar: GitHub Spec Kit is in Assess; teams experiment with it "mostly in brownfield environments" [snippet]. — [Thoughtworks Spec Kit blip](https://www.thoughtworks.com/en-ec/radar/languages-and-frameworks/github-spec-kit)
- [2025 only] Birgitta Böckeler, "Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl" (15 Oct 2025, no later update on the page): defines spec-first / spec-anchored / spec-as-source; distinguishes specs from the "memory bank" (rules files, product descriptions that apply to all sessions). Critiques: problem-size mismatch (Kiro turned a small bug into 4 user stories and 16 acceptance criteria; "a sledgehammer to crack a nut"); review overload ("I'd rather review code than all these markdown files"); false sense of control (agents skipped instructions, generated duplicates of existing classes, over-applied constitution rules); risk of inheriting "the downsides of both MDD and LLMs". — [martinfowler.com](https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)
- Böckeler and Laura Tacho discussed SDD on the Thoughtworks Technology Podcast in May 2026 [snippet; episode not listened to/transcribed]. — [Thoughtworks podcast](https://www.thoughtworks.com/insights/podcasts/technology-podcasts/what-is-spec-driven-development)
- [2025 only] Anthropic, "Effective context engineering for AI agents" (29 Sep 2025): context rot = recall accuracy falls as the window fills; models have an "attention budget"; aim for "the smallest possible set of high-signal tokens"; prefer just-in-time retrieval via lightweight references (file paths) and progressive disclosure; Claude Code is a hybrid ("CLAUDE.md files are naively dropped into context up front", glob/grep fetch the rest); structured note-taking outside the window; sub-agents return condensed summaries; "do the simplest thing that works". — [Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- Practitioner post (14 Feb 2026) says context rot begins well before the token limit and recommends a root file that is an index with task-specific guidance in on-demand files [snippet]. — [tianpan.co](https://tianpan.co/blog/2026-02-14-writing-effective-agent-instruction-files)

### Inferences
- The plugin's core thesis (one canonical set, archive ignored, ADR chain for contradictions) is exactly the mitigation the Radar asks for against "documentation sprawl": a rule for which markdown is authoritative. That is a positioning argument the plugin can cite.
- The same evidence is a warning for the plugin itself: the managed CLAUDE.md block is paid for on every session. It should stay near its current size, and anything that can be a hook or a linter rule should move out of prose.
- The paper finding that "repository overviews do not help" but "agents follow instructions" suggests the CLAUDE.md block should contain only behavior-changing rules (authority order, where to look, never treat archive as current) and no project description.
- Böckeler's "problem-size mismatch" implies a gap if the convention demands a spec/ADR update for every change regardless of size; a size/triviality escape hatch is the commonly implied fix.
- "Harness quality evaluation" (Assess) implies the plugin's hook and linter should themselves be tested for whether they change agent behavior, not assumed to work.

### Gaps
- No 2026 martinfowler.com article by Böckeler specifically on SDD or doc rot was found; the October 2025 piece remains the reference. A January 2026 Fowler fragment endorsing Kent Beck's critique of SDD was seen only through a third-party summary and is not cited here.
- I did not open the full paper PDF, so exact per-agent success deltas in v3 are unverified.
- No empirical study was found that measures whether *specs* (as opposed to AGENTS.md-type files) improve agent task success, nor any study of stale-doc harm with quantified effect.
- A second paper, "Agent READMEs: An Empirical Study of Context Files for Agentic Coding", surfaced only as a reference; not verified.

## 2. Spec/doc drift detection tools and code-path-to-doc mapping

### Takeaway
By late 2026 there is a recognizable pattern: docs declare the code paths they cover in frontmatter (`covers:` globs), a deterministic check compares a git diff or content hashes against that map and fails CI, and an optional LLM pass judges semantic staleness. Tools implementing this are young and small; commercial products (Mintlify, Swimm) instead generate doc-update PRs.

### Cited Findings
- Codocia (Rust crate; 0.1.1 on 2026-05-04, 0.2.0 on 2026-10-30): each markdown page lists `covers:` in YAML frontmatter (e.g. `crates/runtime/**`, or an exact file). `codocia snapshot` hashes covered files into `docs/.codocia-snapshot.json`; `codocia check --base main` exits non-zero on: broken covers (glob matches nothing), stale docs (covered file hash changed), missing covered files, changed code without docs coverage, uncovered code files. Ships an agent skill and a prescribed agent loop. Explicitly no AI calls in the MVP, and states "A passing check means the docs snapshot is current, not that the prose is perfect." — [docs.rs codocia](https://docs.rs/crate/codocia/0.1.1)
- DocPulse (open source GitHub Action): checks a PR diff against docs, `check` exits 1 when a doc section is stale, can commit fixes to the PR branch ("self-healing docs") [snippet]. — [GitHub DocPulse](https://github.com/YoniRaviv/DocPulse)
- `@whenlabs/stale` (npm): scans README/CONTRIBUTING and similar against the code, exits 1 for CI gating, JSON/Markdown output for PR comments [snippet]. — [socket.dev listing](https://socket.dev/npm/package/@whenlabs/stale)
- "Doc Drift Detector" Claude skill (borghei): Python scripts that map code directories to docs, produce a 0-100 staleness score with severity levels and link validation, and can fail CI above a threshold [snippet]. — [skill page](https://borghei.github.io/Claude-Skills/skills/engineering/doc-drift-detector.html)
- Practitioner guides on running doc-rot detection in CI with an LLM agent: "Doc Drift Detection in CI" and "Automated Doc-Rot Detection and Repair with Codex CLI" (26 Apr 2026) [snippets, not opened]. — [understandingdata.com](https://understandingdata.com/posts/doc-drift-detection-ci/); [codex.danielvaughan.com](https://codex.danielvaughan.com/2026/04/26/codex-cli-doc-rot-detection-automated-documentation-repair/)
- Mintlify agent / Autopilot: a workflow in the code repo calls the agent API; the agent opens a PR in the docs repo (or commits directly, per setting); related edits are grouped into one docs PR; authors of the source change are assigned as reviewers. Vendor description [snippet]. — [Mintlify blog](https://mintlify.com/blog/autopilot); [Mintlify agent docs](https://mintlify.com/docs/agent)
- Swimm: "code-coupled" docs with smart tokens tied to code elements; Auto-sync applies mechanical edits such as renames. Secondary source only [snippet]. — [Augment Code guide](https://www.augmentcode.com/guides/self-updating-documentation-docs-agents-sync)
- joestump/claude-plugin-sdd, ADR-0023 (accepted 2026-05-01): a competing Claude Code SDD plugin stores artifact edges in frontmatter (ADRs: `supersedes`, `extends`, `enables`, `governs`, `related`; specs: `implements`, `requires`, `extends`, `supersedes`), derives reverse edges instead of authoring them, links code to artifacts through "governing comments", and exposes `/sdd:graph` with `impact`, `ancestors`, `chain`, `orphans` (code without governing artifact, specs without code, ADRs without specs), `cycles`, and `backfill`. It names `/sdd:check` and `/sdd:audit` as drift/audit commands. — [claude-plugin-sdd ADR-0023](https://joestump.github.io/claude-plugin-sdd/decisions/ADR-0023-frontmatter-dag-and-graph-skill)
- Codeminer42 field report (16 Oct 2026): 289 ADR citations in code comments were audited; a deterministic `adr:check` plus an agent review skill that "compares code against the records covering the changed code, not only those cited"; three PRs passed tests and `adr:check` while the code had drifted from accepted records, and were caught only by semantic review. — [Codeminer42 blog](https://blog.codeminer42.com/stale-docs-are-prompt-injection-you-wrote-yourself/)
- OpenSpec: drift is described by reviewers as its dominant complaint, since "nothing alerts you when a spec no longer reflects reality"; the archive step (merging ADDED/MODIFIED/REMOVED deltas into the living spec) is the only anti-drift mechanism and "should be treated as part of done"; some users add a CI job that fails an archive that did not update the living spec [snippets]. — [codemyspec.com OpenSpec explained](https://codemyspec.com/blog/openspec-explained); [rywalker.com research note](https://rywalker.com/research/openspec)

### Inferences
- The sdd-convention Stop hook detects "code changed" but, as described, has no map from changed paths to the owning spec. A `covers:`/`paths:` list in spec frontmatter would let the hook and linter name the specific spec to update, and would enable four cheap deterministic checks: broken globs, changed code with stale spec, changed code with no owning spec, and (optionally) a coverage ratio.
- Two mechanisms for "stale" exist: diff-based (did the PR touch covered code without touching the spec?) and hash-snapshot (Codocia). Diff-based fits a hook/CI plugin with no extra state; the snapshot approach also catches drift that predates the tool.
- Deterministic checks only establish that someone looked; they do not establish that the prose is true. The Codeminer42 result (three drifted PRs passing the deterministic check) is the best available evidence that an LLM review step adds real detection.
- Comment-based code-to-spec links (governing comments, ADR citations) create a second thing that rots; frontmatter globs on the doc side are cheaper to lint.

### Gaps
- No independent benchmark of any drift tool's precision/recall was found. All tool claims are self-reported; DocPulse, stale, DriftGuard-type projects look like single-author or hackathon work.
- No 2026 primary source from Swimm was retrieved; DocuWriter and "Driftcheck" were not found in results at all.
- Nothing found on a "docs coverage" metric used as an established industry practice beyond Codocia's "uncovered code files" category.
- I could not verify how CODEOWNERS is being reused for spec ownership; no source found.

## 3. ADR ecosystem and agent-oriented decision records

### Takeaway
MADR 4.0.0 (September 2024) is still the reference template and it has no structured `supersedes` field: supersession is free text inside `status`. Frontmatter relation fields (`supersedes`/`superseded-by`) are a community convention with several incompatible spellings. The best 2026 field report recommends exactly the plugin's model (immutable merged records, supersede instead of edit) and adds generated indexes, superseded records excluded from the agent index, and CI that fails edits to merged records.

### Cited Findings
- [2024, still current] MADR current release is 4.0.0 (2024-09-17). Optional YAML frontmatter fields: `status`, `date`, `decision-makers`, `consulted`, `informed`. Status is a free string: "proposed | rejected | accepted | deprecated | … | superseded by ADR-0123". There is an optional `### Confirmation` section asking how compliance with the decision is verified (review, or a test such as ArchUnit). Tooling listed: markdownlint config and the `madr` npm package. — [adr.github.io/madr](https://adr.github.io/madr/)
- Community plugins diverge on supersession frontmatter: one writes `supersedes` on the new ADR and `status: superseded` + `superseded-by` on the old; another uses only a `supersedes` list on the new record [snippets from skill listings]. — [skillselion ADR plugin listing](https://skillselion.com/skills/musingfox/cc-plugins/adr)
- joestump/claude-plugin-sdd ADR-0023 (2026-05-01) takes the position that edges are authored forward-only and reverse edges are derived, never written by hand. — [claude-plugin-sdd ADR-0023](https://joestump.github.io/claude-plugin-sdd/decisions/ADR-0023-frontmatter-dag-and-graph-skill)
- Codeminer42 (16 Oct 2026), observed ADR failure modes in a multi-stack repo used with agents: duplicate ADR numbers; seven phrasings for four relation types in the status column; five accepted records edited in place to read as current, hiding when and why decisions changed; ADRs contradicting the repo (one mandated Conventional Commits while 178 of the last 200 commits used ticket prefixes); 225 of 289 code citations pointing to ambiguous numbers; more than half the index file was table padding; agents opened individual records far more often than the index, so stale records shaped behavior. — [Codeminer42 blog](https://blog.codeminer42.com/stale-docs-are-prompt-injection-you-wrote-yourself/)
- Same source, mitigations: write an ADR only when a choice "could be undone without knowing why it was made"; one decision per file, Nygard-style template; status and relations in frontmatter, relation declared once; "Merged records are immutable. Treat an ADR like a migration that already ran" (only a frontmatter relation and a one-line superseded note may change); IDs assigned by a command; index generated from frontmatter with CI failing if the committed index differs; superseded records dropped from the agent-facing index; records capped around 800 words (CI warning); non-decision knowledge routed to a separate wiki; deterministic script checking duplicate IDs, invalid statuses, one-directional or missing relations, index drift, broken links, and any edit/delete/rename of a merged record; citations to superseded records produce warnings, including in CLAUDE.md and skills; checkable decisions become lint rules with a shrinking baseline and a canary violation per rule. — [Codeminer42 blog](https://blog.codeminer42.com/stale-docs-are-prompt-injection-you-wrote-yourself/)
- A TechRxiv preprint, as relayed by vendor Qodo, reports agents given decision records with rationale used 10.1% less development time and 10.8% fewer tool calls and wrote 16-25 end-to-end tests where the baseline wrote none [snippet; preprint not located or verified]. — [Qodo glossary](https://www.qodo.ai/glossary/what-is-an-architecture-decision-record/)
- A Codex-oriented guide (28 Apr 2026) recommends MADR for agent-generated ADRs, recording which agent/model drafted a decision, keeping ADR text behind a pointer in AGENTS.md, and having the agent stop and propose an ADR before adding a dependency; it attributes to OpenAI's September 2026 Codex guidance a warning against making agents read architecture docs before every edit [snippet; the date ordering (April article citing September guidance) suggests the page was updated or the summary is unreliable]. — [codex.danielvaughan.com](https://codex.danielvaughan.com/2026/04/28/codex-cli-architecture-decision-records-adr-automated-governance/)
- Thoughtworks Radar Vol. 35 (Nov 2026) "Semantic review of AI-edited prose" (Assess): agents revise specs, ADRs and plans "far faster than humans can review them" and "text diffs bury intent under rewording and formatting noise"; an LLM flags meaning changes (altered facts, conflicting statements, redefined acceptance criteria, scope changes), runnable as an agent skill whenever an agent edits a document. — [Thoughtworks blip](https://www.thoughtworks.com/radar/techniques/semantic-review-of-ai-edited-prose)

### Inferences
- The plugin's `supersedes` chain and "never delete an ADR" rule match the strongest practitioner evidence, but two parts are convention-only unless enforced: (a) immutability of accepted ADRs (lintable via git diff: body changes to an `accepted` ADR fail), and (b) bidirectional consistency (new ADR `supersedes: X` implies X has `status: superseded`).
- A generated `docs/decisions/README.md` and `docs/specs/README.md` checked for drift in CI would remove a hand-maintained index, which the field report says "drifts in the first busy week". Excluding superseded ADRs from the index aligns with "archive is ignored by default".
- "Agents opened individual records more often than the index" means index-level filtering is not sufficient; a status banner at the top of superseded/archived files (first lines the agent reads) or physically moving them is needed. The plugin moves archived specs but, per its rules, leaves superseded ADRs in place.
- The plugin rule "edit the spec in place" maximizes exposure to silent meaning changes by agents; semantic diff review of spec edits is the matching control.
- MADR's `Confirmation` section is a ready-made slot for "how is this decision verified" and a bridge from ADR to lint rule or test.

### Gaps
- adr-tools, log4brains, Structurizr, Backstage ADR plugin: no 2026 primary information retrieved about releases or about how they parse supersession. Unknown whether any is actively maintained in 2026.
- No source found for "AgDR" (agent decision record) as a named standard, nor for Y-statements being adopted in agent workflows.
- No standard cross-tool frontmatter schema for `supersedes` exists that I could find; MADR's own tooling page was not opened.

## 4. Requirement formats and verifiability

### Takeaway
EARS is the format most visibly adopted in agent tooling (Kiro), and by August 2026 Kiro links each requirement to derived correctness properties and property-based tests. Evidence that these formats improve outcomes is vendor-supplied; independent critique says they inflate small tasks.

### Cited Findings
- Kiro feature specs write `requirements.md` in EARS; Kiro's docs claim each requirement "can be directly translated into test cases" and tracked through implementation. — [Kiro feature specs docs](https://kiro.dev/docs/specs/feature-specs/)
- Kiro "correctness" docs (page updated 4 Aug 2026): during design Kiro extracts testable properties from EARS requirements (e.g. "For any authenticated user and any active listing, the user can view that listing"), generates property-based tests, and shows links from property to originating requirement and task; the tests are optional by default; on failure the user chooses to fix the code, the test, or the requirement. — [Kiro correctness docs](https://kiro.dev/docs/specs/correctness/)
- OpenSpec structures change proposals as ADDED/MODIFIED/REMOVED requirement deltas merged into a living spec at archive time [snippet]. — [codemyspec.com OpenSpec explained](https://codemyspec.com/blog/openspec-explained)
- A competing vendor (CodeMySpec) argues EARS is narrower than its hype and positions BDD specs checked against the running app as a mandatory gate [snippet; competitor source]. — [codemyspec.com Kiro specs](https://codemyspec.com/blog/kiro-specs-explained)
- "GEARS", an EARS-derived syntax aimed at AI coding, is being promoted on DEV Community [snippet; not opened, date unknown]. — [dev.to GEARS](https://dev.to/sublang/gears-the-spec-syntax-that-makes-ai-coding-actually-work-4f3f)
- [2025 only] Böckeler observed Kiro generating 4 user stories and 16 acceptance criteria for a small bug fix. — [martinfowler.com](https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)
- MADR's optional Confirmation section is the ADR-side equivalent of a verifiability hook (review or automated test such as ArchUnit). — [adr.github.io/madr](https://adr.github.io/madr/)

### Inferences
- The lightest variant with visible uptake is: stable requirement IDs inside the living spec, EARS-style phrasing for the normative statements only, and a trace from ID to at least one test. That is lintable (every `REQ-n` in an active spec is referenced by a test file) without adopting a full SDD tool.
- Requirement-level IDs also make spec drift detection finer-grained than file-level `covers:` globs; the competing plugin explicitly deferred requirement-level edges, suggesting it is costly.
- Forcing EARS/Gherkin on every change would reproduce the problem-size mismatch; it should be optional or limited to MUST-level behavior.

### Gaps
- No independent 2026 study found comparing EARS vs Gherkin vs free prose for agent task success.
- No data on adoption rates of property-based tests from specs outside Kiro.
- Kiro product-timeline claims in secondary sources conflict (announced 2025 vs "launched internationally May 2026"); not resolved.

## 5. Agent memory and context conventions

### Takeaway
The converging 2026 convention is a short root instruction file acting as an index, path-scoped rule files loaded when matching files are touched, and on-demand retrieval of everything else. Path-scoped loading in Claude Code has documented reliability gaps (subagents, malformed frontmatter), so it cannot be the only delivery channel.

### Cited Findings
- Thoughtworks Radar Vol. 35 (Nov 2026): "Progressive context disclosure" in Adopt; "Agent-maintained knowledge bases" in Trial (linked plain-text files maintained by the agent, still needing regular human upkeep); "Subagents for better context management" in Trial; "Agent plugin marketplace" in Trial as a way to distribute harness assets; "Agent suggestion box" in Assess (a place for a running agent to report problems it hits). — [Thoughtworks Radar Techniques](https://www.thoughtworks.com/en-sg/radar/techniques)
- AGENTS.md: reported as natively parsed by over 18 tools in early 2026, with Claude Code a holdout using CLAUDE.md [snippet]; the usual bridge is a CLAUDE.md that imports `@AGENTS.md`; Codex and Claude Code concatenate nested files [snippets]. — [tianpan.co Feb 2026](https://tianpan.co/blog/2026-02-14-writing-effective-agent-instruction-files); [Augment Code guide](https://www.augmentcode.com/guides/agents-md-vs-claude-md)
- Claude Code `.claude/rules/*.md` use a `paths:` frontmatter field (Cursor uses `globs`); rules without `paths` load at launch like CLAUDE.md [snippet]. — [SSW rules](https://www.ssw.com.au/rules/scoped-rules-for-ai-agents)
- Reported problems with path-scoped rules: an issue reports all rule files loading at startup regardless of `paths:`; another reports path-specific rules not loading in subagents, teammates or skill-forked contexts; malformed frontmatter fails open and the rule loads every session [snippets; behavior may have changed, verify against current Claude Code]. — [issue 15710 mirror](https://claudeissues.com/issue/15710-documentation-feature-paths-frontmatter-in-claude-rules-does-not-enable-lazy-loa); [issue 32906 mirror](https://claudeissues.com/issue/32906-docs-path-specific-rules-do-not-load-in-subagents-teammates-or-skill-forked-cont)
- [2025 only] Anthropic: keep lightweight references (paths) and load on demand; use file names, sizes and timestamps as navigation cues; persistent notes outside the window. — [Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- The competing SDD plugin explicitly declined to build a local MCP server or embedding search for specs, treating the frontmatter graph as the contract a future MCP would consume (May 2026). — [claude-plugin-sdd ADR-0023](https://joestump.github.io/claude-plugin-sdd/decisions/ADR-0023-frontmatter-dag-and-graph-skill)
- Codeminer42 (Oct 2026): keeps the agent-facing ADR index lean, generated, and without superseded entries; separate `docs/wiki/` store for gotchas and procedures. — [Codeminer42 blog](https://blog.codeminer42.com/stale-docs-are-prompt-injection-you-wrote-yourself/)

### Inferences
- The plugin's `docs/specs/README.md` and `docs/decisions/README.md` indexes are the progressive-disclosure pattern the Radar puts in Adopt. Their value depends on being generated and current, and on each entry having a one-line "when to read this" so the agent can choose.
- The plugin is Claude Code-specific (CLAUDE.md block, Stop hook). A parallel AGENTS.md block or an `@`-import is the low-cost way to reach other agents.
- A path-scoped rule ("when editing `src/payments/**`, the owning spec is `docs/specs/payments.md`") could be generated from spec `covers:` frontmatter, giving just-in-time injection; given the reported gaps, a PreToolUse/PostToolUse hook doing the same lookup is the more dependable channel.
- An MCP server for specs looks premature for small repos: a peer project considered and deferred it, and file-based retrieval already matches Anthropic's guidance.

### Gaps
- llms.txt adoption in 2026: no results; cannot say whether it matters for in-repo agent context.
- Cline memory bank: no current description retrieved; status in 2026 unknown.
- Diátaxis applied to agent docs: no source found.
- No measurement found of session-start injection (SessionStart hook) vs on-demand reading for doc truthfulness.
- AGENTS.md adoption figure comes from a single blog snippet; no primary count verified.

## 6. Enforcement patterns

### Takeaway
Practitioners are converging on a layered model: deterministic checks first (lint, CI, hooks that block), LLM review second for meaning, human sign-off last. Reminder-only hooks are widely reported as insufficient.

### Cited Findings
- Codeminer42 (16 Oct 2026): "A rule that nobody checks doesn't hold"; deterministic checks run first, then an agent review skill for meaning, then "AI checks; humans attest"; CI fails on index drift and on edits to merged ADRs. — [Codeminer42 blog](https://blog.codeminer42.com/stale-docs-are-prompt-injection-you-wrote-yourself/)
- Thoughtworks Radar (Nov 2026): convert instructions into deterministic hooks or checks; evaluate that the harness actually works; "Feedback flywheel" in Trial with the note that teams also need to remove rules that no longer help. — [Thoughtworks Radar Techniques](https://www.thoughtworks.com/en-sg/radar/techniques)
- Codocia's `check --base main` exits non-zero and is designed for both CI and the agent's own loop (run check, read policy, update prose only when the diff changes documented behavior, re-snapshot). — [docs.rs codocia](https://docs.rs/crate/codocia/0.1.1)
- OpenSpec users describe treating the archive step as part of the definition of done and adding CI that fails an archive that did not update the living spec [snippet]. — [codemyspec.com OpenSpec explained](https://codemyspec.com/blog/openspec-explained)
- Mintlify assigns the author of the source-code change as reviewer of the generated docs PR [snippet, vendor]. — [Mintlify blog](https://mintlify.com/blog/autopilot)
- Community posts argue for enforcing rules with hooks that block (PreToolUse, Stop with a blocking decision) instead of prose, and describe a Stop hook that scans the transcript tail and injects a system message on violation [snippets]. — [bitbytebit substack](https://bitbytebit.substack.com/p/agent-hooks-deterministic-guardrails); [dev.to krisnamic](https://dev.to/krisnamic/stop-telling-claude-code-rules-enforce-them-with-hooks-3po1)
- Qodo (vendor) argues an ADR only matters if code review checks against it [snippet]. — [Qodo glossary](https://www.qodo.ai/glossary/what-is-an-architecture-decision-record/)

### Inferences
- The plugin has two of the three layers in weak form: a linter (deterministic, but about document shape, not code-to-spec consistency) and a Stop hook (a nudge). Missing: a CI/pre-commit gate that fails when covered code changes without the owning spec or an ADR changing, with an explicit override (e.g. a commit trailer or PR label such as "no-spec-change" plus a reason), and an optional review subagent comparing the diff to the owning spec.
- An override path matters: without it a hard gate produces noise edits to specs, which is itself documentation rot.
- The Stop hook would be more effective if it named the specific spec file (from `covers:`) and stayed silent when no covered code changed, lowering reminder volume.

### Gaps
- No source found describing PR-template or bot-based "spec/ADR updated?" checkboxes with measured compliance.
- No source found that evaluates review subagents for spec compliance with numbers; the Codeminer42 report gives three caught PRs, with no false-positive rate.
- Search for a dedicated "spec compliance reviewer subagent" pattern returned nothing specific.

## 7. Reported failure modes of doc-convention approaches and mitigations

### Takeaway
The recurring failures are: agents not following prose rules (especially after compaction and inside subagents), acknowledged-then-ignored Stop hooks, stale docs being read as instructions, silent in-place rewrites, markdown volume overwhelming reviewers, and token cost. Mitigations cluster around fewer words, more determinism, immutability, generated indexes and semantic review.

### Cited Findings
- Agents ignoring prose rules: GitHub issue reports of CLAUDE.md "MUST/ALWAYS" rules not followed, and of rules followed before context compaction but ignored afterward with no warning; one draft issue claims roughly half of sessions (anecdotal, not measured) [snippets]. — [issue 19471 mirror](https://claudeissues.com/issue/19471-bug-claude-md-instructions-completely-ignored-after-context-compaction); [issue 2544 mirror](https://claudeissues.com/issue/2544-bug-claude-md-mandatory-rules-consistently-ignored-across-multiple-repositories)
- Stop hooks ignored: a Hacker News "Tell HN: Claude 4.7 is ignoring stop hooks" post describes a Stop hook telling the agent to run tests that the agent acknowledged and then ignored again a few turns later [snippet; single anecdote]. — [HN mirror](https://hn.nuxt.dev/item/47895029)
- Path-scoped rules not reaching subagents; malformed frontmatter failing open [snippets]. — [issue 32906 mirror](https://claudeissues.com/issue/32906-docs-path-specific-rules-do-not-load-in-subagents-teammates-or-skill-forked-cont)
- Stale docs acting as instructions: "That's prompt injection, except nobody attacked you. You wrote it yourself, months ago, and never went back."; superseded records in the index "consumed context without giving the agent anything useful"; agents read individual records more than the index (16 Oct 2026). — [Codeminer42 blog](https://blog.codeminer42.com/stale-docs-are-prompt-injection-you-wrote-yourself/)
- Silent rewriting of history: five accepted ADRs edited in place to look current (16 Oct 2026). — [Codeminer42 blog](https://blog.codeminer42.com/stale-docs-are-prompt-injection-you-wrote-yourself/)
- Over-documentation and review fatigue: Radar "AI-driven documentation sprawl" (Caution, Nov 2026); Radar "Semantic review of AI-edited prose" (Assess, Nov 2026) cites review fatigue as the motive; Böckeler [2025 only] on verbose repetitive markdown. — [Thoughtworks sprawl blip](https://www.thoughtworks.com/radar/techniques/ai-driven-documentation-sprawl); [Thoughtworks semantic review blip](https://www.thoughtworks.com/radar/techniques/semantic-review-of-ai-edited-prose); [martinfowler.com](https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)
- Token cost: over 20% average inference cost increase from context files (2026). — [arXiv 2602.11988](https://arxiv.org/abs/2602.11988)
- Rule accumulation: instructions grow, conflict and go stale; prune with each new model and remove rules that no longer help (Nov 2026). — [Thoughtworks instruction bloat blip](https://www.thoughtworks.com/radar/techniques/agent-instruction-bloat)
- False confidence from passing checks: three drifted PRs passed tests and the deterministic ADR check (Oct 2026); Codocia warns a passing check does not mean the prose is right (2026). — [Codeminer42 blog](https://blog.codeminer42.com/stale-docs-are-prompt-injection-you-wrote-yourself/); [docs.rs codocia](https://docs.rs/crate/codocia/0.1.1)
- Spec drift in convention-only SDD tools: OpenSpec specs "don't self-update during implementation" and are "a strong convention, not a hard contract" [snippets]. — [rywalker.com research note](https://rywalker.com/research/openspec)

### Inferences
- Mapping failure mode to candidate mitigation for the plugin:
  - Rules ignored after compaction or in subagents -> re-inject the short authority block via hook at the moments it matters (session start, post-compaction, subagent start) instead of lengthening CLAUDE.md.
  - Stop-hook nudge ignored -> make the nudge specific (named spec, named changed paths), fire only when covered code changed, and back it with a pre-commit/CI gate that cannot be ignored.
  - Stale doc read directly -> status banner in the first lines of superseded/archived files, generated index excluding them, linter warning on links/citations pointing to superseded or archived docs (including from CLAUDE.md and skills).
  - Silent history rewrite -> immutability check on accepted ADRs; semantic diff review for in-place spec edits.
  - Over-documentation -> ADR threshold ("could be undone without knowing why"), word-count warning, triviality exemption for spec updates, plans genuinely deleted or archived.
  - Token cost -> measure the size of what the plugin injects (context profiling) and set a budget.
- There is no direct evidence for "reminder fatigue" as a named phenomenon in agents; what is documented is non-compliance with reminders. The human-side analogue (review fatigue from markdown volume) is documented.

### Gaps
- All agent non-compliance evidence is anecdotal (issue reports, one HN post). No measured compliance rate for Stop-hook reminders was found.
- No before/after data showing that any mitigation above reduces drift; the Codeminer42 post is a single-team case study.
- Whether newer models (late 2026) are materially better at following hook reminders is unknown from these sources.
