---
name: grill-walk
description: Walk a live artifact or code-grounded substitute, ratify concrete product findings one at a time, and hand a structured evidence record to dispatch-compiler for proof-gated issue filing and closeout. Use when the user says "grill walk", "design walk", "walk the app/site", "punch list session", "grill #N", or wants agent-ready work from product taste and runtime evidence.
---

# Grill Walk

Turn product taste into ratified evidence, then delegate packet generation to
the canonical compiler. This skill owns the walk and the owner conversation.
`dispatch-compiler` owns lane carving, issue schema, model routing, tracker
mutation, and source closeout.

## Non-Negotiables

- Do not fix during the walk. Observe, map, ratify, and record.
- Ratify one consequential product decision at a time.
- Map every finding to concrete territory before it can enter the handoff.
- Preserve vetoes and deliberate non-items so later sessions do not relitigate
  them.
- Follow the target repository's `AGENTS.md` and selected dispatch profile for
  evidence location, tracker labels, runtime ownership, and closeout policy.
- Do not reproduce issue templates, model names, effort rules, GitHub commands,
  or closeout mechanics here. Those belong to `dispatch-compiler` and the
  project profile.

## Phase 0 - Contract

If invoked with an issue number, read the current issue first. Treat its body as
the charter, but re-verify its scope, blockers, prior ratification, and evidence
against current repository state.

Before walking:

1. Read the repository contract and select the applicable dispatch profile.
2. State the session mode: `owner-ratified`, `autonomous`, `code-grounded`, or
   `live-walked`. Combine origins when more than one is true.
3. State the output contract: this phase produces a structured compilation
   handoff; the compiler decides safe lane shape and tracker routing afterward.
4. Choose a durable evidence location allowed by the repository contract.
5. If the owner compares the artifact with an elevated vision, apply the recall
   test: only details they can name are admissible, with at most one or two
   elevation cherry-picks per session.
6. If recommendations depend on research, gather or read attributable research
   before proposing decisions.

## Phase 1 - Walk

- Drive the real artifact when practical: browser, simulator, device, docs,
  email, store listing, or generated preview. Use realistic locale, theme,
  authentication state, platform, viewport, and data.
- Walk daily-use surfaces before first-run flows that disturb state. Keep each
  screen brief: early reactions reveal taste; prolonged staring invents noise.
- Prime each surface with two to four concrete observations to confirm or
  dismiss, then ask what bothers the owner.
- For every candidate, immediately map files, routes, components, strings,
  tokens, tests, screenshots, recordings, logs, or artifact paths.
- Record the observed behavior, proposed outcome, buy or veto, evidence origin,
  confidence, and any deliberate non-item.
- If an entire surface needs judgment, capture obvious mechanical findings and
  record a separate unresolved owner call instead of forcing a full redesign.
- If live driving stalls, pivot to current code and artifacts. Record the
  blocker and mark the origin `code-grounded` or `artifact-grounded` rather
  than pretending it was live-walked.

## Phase 2 - Rank

Rank findings for dispatch usefulness:

1. Broken behavior a new user will encounter.
2. Systemic problems and daily-surface fixes.
3. High-risk correctness involving auth, data, native behavior, payments, or
   release/runtime compatibility.
4. Visual and copy polish, riders, and verify-only checks.
5. At most one elevation cherry-pick per session.

Ranking is evidence for the compiler, not a pre-carved lane plan. Record likely
sequencing or territory collisions, but let the compiler produce the final
file-disjoint issue set. Verify-only observations normally become proof gates
inside related work rather than standalone implementation issues.

## Phase 3 - Compilation Handoff

Produce this record without omitting empty or blocked sections:

```markdown
## Compilation handoff

- Source repository and source issue:
- Session mode and evidence origin:
- Overall confidence:
- Project profile:

### Ratified findings

- Finding, expected outcome, confidence, and owner decision:

### Vetoes and deliberate non-items

- Decision and reason:

### Evidence and artifact paths

- Path or URL and what it proves:

### Territory anchors

- Finding -> files, routes, components, strings, tests, or artifacts:

### Ranking and sequencing observations

- Rank, likely collision, or dependency:

### Unresolved owner calls

- Decision still required and concrete options already considered:

### Runtime proof status and blockers

- What was driven, what was not, blocker, and acceptable substitute evidence:
```

**REQUIRED SUB-SKILL:** invoke `dispatch-compiler` in the same task after the
handoff is complete. Pass the handoff intact and name the selected project
profile. The compiler must re-verify current anchors, carve merge-safe lanes,
generate packet-specific Codex and Claude routing, file or update tracker work
as authorized by the repository policy, and close out the source charter when
its close conditions are satisfied.

Do not re-ratify bought decisions during compilation. If current evidence
contradicts a ratified finding, preserve the decision record, stop that finding
from becoming `ready`, and report the contradiction through the compiler's
normal status and closeout rules.
