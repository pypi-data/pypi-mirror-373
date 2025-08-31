### CerebraFlow Unified CLI Agent Loop Implementation Plan (Fowler‑aligned)

Reference: [Building your own CLI Coding Agent with Pydantic‑AI](https://tracking.tldrnewsletter.com/CL0/https:%2F%2Fmartinfowler.com%2Farticles%2Fbuild-own-coding-agent.html%3Futm_source=tldrwebdev/1/01000198f0691548-18c31833-3176-442d-9483-1fea2a8d53b0-000000/9mTnUagldPRXwcmtww2guqpC_aBR_dte89oI8fJqGPM=420)

#### Goal
Implement a cohesive developer agent loop for CerebraFlow that mirrors the article’s capabilities while preserving VEG/AEMI, uv/.venv, and ChromaDB‑first architecture. Deliver a small CLI orchestration (“cflow agent”), focused MCP tools, instruction profiles, and documentation. This file will be parsed to create tasks once the Cflow migration to its separate repository completes.

#### Build Order
- Build Cflow portions first. Platform‑level add‑ons (AWS MCP pack, desktop notifications) are optional and can follow without blocking the core loop.

#### Core Loop (from article)
- run tests → inspect failing tests → read implementation → fetch docs → make minimal edits → lint → re‑run tests → repeat.
- Named capabilities analogs to include: `run_python`/sandboxed execution, `code_reasoning` planning, Context7 docs integration, optional AWS MCPs, optional desktop notifications.

---

### Progress Tracker

- [/] Phase 1: Cflow Core Agent Loop
  - [/] 1.1 MCP tool: testing.run_pytest
    - [x] 1.1.1 Design spec: testing.run_pytest schema and truncation policy (VEG Gate 1 complete)
    - [x] 1.1.2 Implement pytest executor (uv, non‑interactive, size caps)
    - [x] 1.1.3 Implement log parser (summary JSON)
    - [x] 1.1.4 Add CLI subcommand wiring and help
    - [x] 1.1.5 Unit tests for runner + parser
  - [/] 1.2 CLI entrypoint: cflow agent (default loop orchestrator)
  - [ ] 1.3 Failure parser and report synthesizer
  - [ ] 1.4 Minimal edit applier (file‑scoped, SRP)

---

## Phase 1: Cflow Core Agent Loop (High priority)

- 1.1 MCP tool: testing.run_pytest (uv pytest with summarized output)
  - Description: Non‑interactive `uv run pytest -xvs tests/` with stdout/stderr capture, truncation, and a failure summary (test name, file:line, error type, top lines of trace).
  - Inputs: path/markers; truncation limits; verbosity.
  - Outputs: raw logs; structured JSON summary; boolean pass/fail.
  - Acceptance:
    - Executes within `.venv` using `uv` only; no interactivity; no pager.
    - Handles large output with safe truncation and clear “truncated” markers.
    - Returns pass/fail plus a de‑duplicated, structured failure list.

- 1.2 CLI entrypoint: cflow agent (default loop orchestrator)
  - Description: Orchestrates RAG context pull → run_pytest → parse → minimal edits → lint → run_pytest → report. Prints short plan, diffs applied, and final status.
  - Inputs: flags (e.g., `--profile=strict`, `--docs=auto`, `--dry-run`).
  - Outputs: console report; optional JSON report for CI.
  - Acceptance:
    - Single command performs end‑to‑end loop.
    - Honors pre‑commit; aborts on violations (no `--no-verify`).
    - Supports dry‑run with diff preview before apply.

- 1.3 Failure parser and report synthesizer
  - Description: Parse pytest logs to structured errors (test id, file:line, error type, message, top trace); de‑duplicate; map to files/functions.
  - Acceptance:
    - Correctly parses common pytest patterns (>95%).
    - Produces actionable mapping from failure → candidate files/functions.

- 1.4 Minimal edit applier (file‑scoped, SRP)
  - Description: Apply targeted edits returned by reasoning tool with safety checks (allowlisted paths, conflict detection), dry‑run support, and revert on failure.
  - Acceptance:
    - Never writes outside allowlisted directories.
    - Aborts on merge conflicts; prints unified diffs; supports rollback.

---

## Phase 2: Reasoning + Instruction Profiles

- 2.1 Instruction profiles loader
  - Description: Load instruction blocks (e.g., “fix implementation before tests”, “minimal diffs”, SRP) from project rules (`.cursor/rules` and workspace rules). Inject into agent loop.
  - Acceptance:
    - Profile applied every run; toggle via `--profile`.
    - Deterministic precedence rules (project > workspace defaults).

- 2.2 MCP tool: code_reasoning.plan
  - Description: Given parsed failures + code snippets, emit a short plan: hypotheses, minimal edits, and verification steps (including success checks and re‑test conditions).
  - Acceptance:
    - Deterministic JSON schema; bounded step count (small, SRP‑compliant).
    - Each step has explicit success criteria and file scope.

- 2.3 Lint and pre‑commit integration step
  - Description: Auto‑run lint/format; present violations; re‑run tests only if lint passes.
  - Acceptance:
    - Honors local pre‑commit hooks; fails closed on violations.

---

## Phase 3: Sandboxed Execution + Docs Auto‑Assist

- 3.1 MCP tool: sandbox.run_python
  - Description: Execute Python snippets via `uv run` with CPU/memory/time caps; filesystem allowlist; no network; clean stdout/stderr.
  - Acceptance:
    - Enforced limits; deny network; fail closed on policy violations.

- 3.2 Context7 auto‑docs in loop
  - Description: On stack traces referencing external APIs/symbols, auto‑fetch relevant docs via Context7 and inject top summaries into the reasoning context.
  - Acceptance:
    - Off by default, enable with `--docs=auto`.
    - Shows top 1–2 doc extracts with source links.

---

## Phase 4: Optional Packs (Off by default)

- 4.1 AWS MCP profile
  - Description: Optional profile enabling AWS Labs MCPs for cloud‑native teams; gated via `--profile=aws`.
  - Acceptance:
    - Disabled by default; clean failure when credentials missing.

- 4.2 Desktop notifications bridge (minimal)
  - Description: Scoped local notifications (e.g., “tests completed”). No system control or file operations.
  - Acceptance:
    - Disabled by default; respects OS notification policies.

---

## Phase 5: Platform Integration & Documentation

- 5.1 Dev workflow integration
  - Description: Wire agent results into existing dev workflow tools (code review, pre‑commit, post‑commit) without duplication.
  - Acceptance:
    - Zero new violations; unchanged hooks behavior; green pre‑commit.

- 5.2 Documentation
  - Description: Add docs under `docs/tools/agent-loop/` for usage, flags, profiles, safety, troubleshooting.
  - Acceptance:
    - Includes examples; governance notes (VEG/AEMI, uv/.venv, ChromaDB‑first).

- 5.3 Telemetry and guardrails
  - Description: Minimal non‑PII telemetry on loop outcomes; configurable opt‑out.
  - Acceptance:
    - Config flag documented; auditability.

---

## AEMI Atomic Breakdown (ready to import post‑migration)

- [x] 1.1.1 Design spec: testing.run_pytest schema and truncation policy
- [x] 1.1.2 Implement pytest executor (uv, non‑interactive, size caps)
- [x] 1.1.3 Implement log parser (summary JSON)
- [x] 1.1.4 Add CLI subcommand wiring and help
- [x] 1.1.5 Unit tests for runner + parser

- 1.2.1 Draft agent loop sequence + flags
- 1.2.2 Implement loop shell (context → tests → plan → edit → lint → tests)
- 1.2.3 Add dry‑run edits + diff presentation
- 1.2.4 Integrate pre‑commit, bail on violations
- 1.2.5 End‑to‑end tests on a sample failing test

- 1.3.1 Failure parser coverage tests (common pytest patterns)
- 1.4.1 Safety checks (allowlist paths, rollback)

- 2.1.1 Define instruction profile schema and discovery
- 2.1.2 Implement loader + precedence
- 2.1.3 Profile unit tests

- 2.2.1 Define plan output schema (hypotheses, steps, success checks)
- 2.2.2 Implement code_reasoning.plan tool
- 2.2.3 Add minimal‑edit constraints (SRP, scope)
- 2.2.4 Plan tool unit tests

- 2.3.1 Lint step integration; fail‑closed behavior

- 3.1.1 Sandbox policy (limits, FS allowlist)
- 3.1.2 Implement sandbox.run_python executor
- 3.1.3 Policy enforcement tests

- 3.2.1 Error → symbol extraction for docs lookup
- 3.2.2 Integrate Context7 fetch + summarization
- 3.2.3 Add toggle, tests

- 4.1.1 AWS profile config and env detection
- 4.1.2 Document profile and safeguards

- 4.2.1 Minimal notifier with OS allowlist
- 4.2.2 Documentation for off‑by‑default operation

- 5.1.1 Dev workflow glue (no duplication)
- 5.2.1 Author docs and examples
- 5.3.1 Add opt‑in telemetry hooks and docs

---

## Task Documentation Template (apply to each atomic task)

```
- Title: <>=15 chars>
- Description: <>=80 chars detailed description, goals, constraints (VEG/AEMI, uv/.venv, ChromaDB‑first)>
- Inputs: <flags, environment, configs>
- Outputs: <artifacts, tool endpoints, docs>
- Dependencies: <task IDs>
- Acceptance Criteria:
  - <deterministic checks, tests to run, success/failure flags>
- Validation Steps:
  - <commands, expected results>
- Risk/Notes:
  - <edge cases, security constraints>
- Estimate: <time>
- Owner: <name>
```

---

## Validation Gates

- Gate A: 1.1 + 1.3 pass; `testing.run_pytest` returns structured JSON with correct pass/fail and truncation markers.
- Gate B: 1.2 e2e: a known failing test is fixed via minimal edit + lint + re‑run → green.
- Gate C: 2.x reasoning: plans are bounded, SRP‑compliant, reproducible; steps include success checks.
- Gate D: 3.x sandbox: limits enforced; no network; FS allowlist respected; policy tests pass.
- Gate E: Docs complete; pre‑commit green; telemetry disabled by default with clear opt‑in.

---

## 1.1.1 Design Spec: testing.run_pytest (Completed)

- VEG/AEMI Gate 1 (Documentation) passed; aligns with Fowler loop and current implementation.
- Tool name: `testing_run_pytest`
- Execution: `uv run pytest -xvs <path>` with optional `-k <markers>`; capture stdout/stderr; non‑interactive; no pager.

Inputs (all optional):

```
{
  "path": { "type": "string", "description": "Tests path; default auto-detects nearest tests/" },
  "markers": { "type": "string", "description": "Pytest -k expression" },
  "max_output_bytes": { "type": "integer", "default": 200000, "description": "Truncate combined stdout+stderr beyond this size and append [TRUNCATED]" },
  "verbose": { "type": "boolean", "default": false, "description": "Include raw_logs in result" }
}
```

Behavior:
- Assemble command: `uv run pytest -xvs <path> [ -k <markers> ]`.
- Capture stdout and stderr; combine in order; apply size cap with `[TRUNCATED]` sentinel.
- Return structured JSON with pass/fail and concise failure summary suitable for agent loop.

Output shape:

```
{
  "status": "success",
  "exit_code": 0,
  "passed": true,
  "truncated": false,
  "summary": {
    "failures": [ { "test": "<id/header>", "trace": "<last 20 lines>" } ],
    "summary_line": "=== 1 failed, 12 passed in 2.34s ==="
  },
  "raw_logs": "... included only when verbose=true ..."
}
```

Constraints & Safety:
- `.venv` + `uv` only; non‑interactive; no pager; deterministic output.
- Handles missing tests path or no tests (non‑zero exit with informative summary).
- Truncation is size‑bounded with explicit marker.

Notes:
- Further gates will validate executor behavior (Gate A), parser coverage (1.3), and end‑to‑end loop (1.2).


## Risks & Constraints

- Must adhere to VEG/AEMI, uv/.venv only, no `--no-verify`, ChromaDB‑first storage.
- Edit applier must never write outside allowlisted directories; dry‑run default for safety.
- Optional packs (AWS, desktop notifications) remain opt‑in; disabled by default.

---

## Capability Alignment (quick)

- Core MCP extensibility: Aligned
- Single CLI agent loop: Delivered via `cflow agent`
- First‑class test runner: `testing.run_pytest`
- Sandboxed Python exec: `sandbox.run_python`
- Up‑to‑date docs: Context7 auto‑assist (opt‑in)
- AWS MCPs: Optional profile
- Desktop notifications: Optional minimal bridge
- Strict execution standards: Enforced

---

## Next Steps (post‑migration)

- Parse this `Fowler-aligned_implementation_plan.md` to seed tasks with IDs, dependencies, and acceptance notes.
- Execute Phases 1 → 2 → 3; then optional packs (4); finalize platform integration and docs (5).


