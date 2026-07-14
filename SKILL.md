---
name: dispatch-compiler
description: Compile a charter, product surface, complaint, research finding, code finding, or artifact into concrete, confidence-labeled, proof-gated successor issues for parallel coding agents. Use when planning Conductor-style or worktree-based agent lanes, running live-walk or artifact-grounded reviews, filing ready/needs-grill/blocked/owner work, adding dispatch calibration blocks, or closing out a source issue with successor grouping and proof requirements.
---

# Dispatch Compiler

Use this skill to turn messy inputs into dispatchable agent work. The goal is
mergeable output, not cheap calls, large backlogs, or speculative tickets.

`examples/worked-example.md` shows one complete pass — a fuzzy owner complaint
compiled into four labeled issues plus a closeout. When runtime proof is
blocked, `examples/worked-example-ci-log.md` shows the artifact-grounded
fallback path. Match that standard of concreteness.

## Load Context

1. Identify the source charter: issue, product surface, complaint, research
   note, code finding, screenshot, log, or artifact.
2. Read the project profile if one exists. Profiles define local labels, proof
   gates, model policy, branch rules, runtime rules, and closeout conventions.
3. Resolve `calibrate-model-routing/scripts/calibration_snapshot.py` relative
   to this skill and run `python3 calibration_snapshot.py status`. Read the
   shared snapshot before assigning current model names.
   - `fresh`: route normally.
   - `stale`: route from the last known-good snapshot and give the user
     one non-blocking reminder to run `$calibrate-model-routing`.
   - `missing` or `invalid`: compile the rest of the packet, mark model routing
     uncalibrated, and tell the user to run the calibrator.
     Do not guess current model names.
4. Re-verify current state before filing or closing anything. Treat old issue
   text, stale screenshots, and prior notes as leads until current evidence
   confirms them.

## Evidence Standard

Prefer live evidence when practical: run the app, walk the product surface,
capture screenshots, inspect logs, or exercise the failing path.

If live proof is blocked, pivot to code-grounded or artifact-grounded evidence:
files, routes, strings, tests, command output, screenshots, recordings, design
artifacts, or logs. Record what blocked live proof and what evidence replaces
it.

Every finding must name at least one concrete anchor:

- file path, symbol, route, endpoint, database object, or UI string
- screenshot, recording, log, command, test, or artifact path
- current behavior and expected behavior
- proof gate that can confirm the work

## Origin Labels

Use one or more origins in each successor issue:

- `owner-ratified`: the owner explicitly agreed this should change.
- `live-walked`: the finding was observed in a running product.
- `code-grounded`: the finding is grounded in current source code.
- `artifact-grounded`: the finding is grounded in a screenshot, log, recording,
  design, document, or exported artifact.
- `autonomous`: the agent inferred the finding without owner ratification.

Autonomous findings usually become `needs-grill` unless they are mechanically
certain and low-risk.

## Status Routing

Route each successor issue honestly:

- `ready`: owner-ratified or mechanically certain, with a concrete proof gate.
- `needs-grill`: the finding is real but owner or product judgment is missing.
  Grill means interrogate: give the owner a crisp decision to make, ideally
  with concrete options, rather than smuggling taste into a ready ticket.
- `blocked`: dispatchable, but blocked by a named issue, condition, access
  gap, dependency, or environment failure.
- `owner`: human-only decision or action.

Do not mark a ticket `ready` just because it is easy. Ease is not certainty.

## Successor Issue Requirements

Use `templates/successor-issue.md` when filing work. Each issue must include:

- charter and expected outcome
- evidence with origin and confidence
- scope boundaries
- file, route, string, command, screenshot, or artifact anchors
- dispatch calibration block
- parallel-safety notes
- escalation triggers
- proof gate and close criteria

If a PR fully completes the issue, instruct the shipping lane to use a GitHub
closing keyword such as `Closes #123`. If the work is partial, use `Refs #123`
and say why the issue remains open.

## Dispatch Calibration

Add this block to every successor issue:

```markdown
## Dispatch calibration

- Origin:
- Confidence:
- Complexity:
- Risk:
- Cost posture:
- Helper agents:
- Parallel safety:
- Escalation triggers:
- Proof gate:

## Model routing

- Codex: <starting model> / <effort> → <escalation model> / <effort> if the packet's escalation condition triggers.
- Claude: <starting model> / <effort> → <escalation model> / <effort> if the packet's escalation condition triggers.
```

Calibrate model usage for the cost of being wrong, not the apparent size of the
diff. No low-end model should own a shipping lane by default. Use cheaper
helpers only for bounded, reviewable work such as search, log reduction,
screenshot inventory, duplicate detection, test runs, or artifact extraction.
Keep frontier or senior-agent review for synthesis, risk, product judgment, and
merge-critical implementation.

## Model Routing

Route Codex and Claude independently from the shared snapshot. Never recommend
one provider over the other.

For each provider:

1. Apply current catalog and effort semantics from the snapshot.
2. Narrow them with project availability and ownership constraints.
3. Choose the least expensive tier that can safely own this packet.
4. Raise model capability for genuine difficulty, unfamiliarity, ambiguity,
   or knowledge limits.
5. Raise effort for inspection depth, tool use, test execution, persistence,
   or verification burden.
6. Select a long-horizon specialist directly when the task is already larger
   than an ordinary sitting.
7. Add an arrow only when a materially stronger available route exists. Point
   it at the packet's existing escalation condition without copying it.

For `owner` or `needs-grill` work with no model-owned execution, emit `Not
applicable until ratified`. Low-cost helpers may own bounded evidence work, but
do not let them own shipping lanes by default.

## Parallel Lane Carving

Before filing issues, group findings into lanes:

1. Prefer file-disjoint or subsystem-disjoint issues.
2. Name sequencing edges explicitly: "Issue B waits for Issue A" or "Can run in
   parallel with #N".
3. Avoid sending multiple lanes to edit the same unstable files at once.
4. Put cross-cutting migrations, shared abstractions, and risky product choices
   behind a higher-confidence lane or owner decision.

If lanes cannot be made safe, say so and file fewer, larger issues.

## Closeout

Use `templates/source-closeout-comment.md` to close the source charter. Include:

- successor issues grouped by label
- dispatch-now vs waiting
- deliberate non-items
- unresolved owner calls
- evidence inspected
- final label and close state
- archive status, if applicable

Close the source issue only when it is consumed by successor issues, superseded
by already-landed work, or intentionally resolved. If it still contains real
product work that no successor issue captures, leave it open and name exactly
what remains.

## Stop Conditions

Stop and report instead of pretending confidence when:

- current code contradicts the charter
- evidence cannot be anchored to files, artifacts, commands, or runtime output
- the requested change depends on owner-only product judgment
- the proof gate cannot be run and no acceptable substitute exists
- lane boundaries require multiple agents to edit the same fragile files
- access, environment, or dependency failures block verification

When blocked, file a `blocked` issue only if the work is otherwise shaped and
the blocker is named. Otherwise ask for the missing decision or access.
