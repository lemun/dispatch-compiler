# On-Demand Model Routing Calibration

Date: 2026-07-14
Status: Approved design
Applies to: `dispatch-compiler`, Claude Code, and Codex

## Summary

Add a manually invoked `calibrate-model-routing` skill and a shared local
calibration snapshot. The calibrator refreshes current model and effort
guidance from official OpenAI and Anthropic sources. `dispatch-compiler` reads
that snapshot and generates a compact, task-specific model-routing block for
each new packet.

Calibration and routing are separate operations:

- Calibration answers: "What models and effort controls are current, and what
  does each provider recommend them for?"
- Routing answers: "Given this packet's work, which model and effort should a
  Codex user start with, and which should a Claude user start with?"

The snapshot is global across repositories and tools. Calibration is manual,
never scheduled. Existing packets are never rewritten.

## Problem

`dispatch-compiler` currently requires these fields in every successor issue:

- `Recommended Claude lane + effort`
- `Recommended Codex lane + effort`

The skill does not define a current model catalog or a repeatable routing
method. Examples use generic labels such as "default lane" and
"frontier lane." This creates three problems:

1. Model names and effort controls change faster than the packet workflow.
2. Agents can copy a default recommendation into every packet instead of
   calibrating it to the task.
3. Putting the full routing rubric into every packet makes packets noisy and
   duplicates complexity, risk, cost posture, and escalation fields that are
   already present.

The desired outcome is current guidance without per-packet research or a large
model-policy appendix attached to every issue.

## Goals

- Provide one memorable, on-demand calibration action.
- Use official OpenAI and Anthropic sources by default.
- Maintain separate recommendations for Codex and Claude users.
- Generate routing from each packet's actual traits.
- Keep the packet output to one compact line per provider.
- Reuse the packet's existing escalation condition instead of repeating it.
- Warn when calibration is stale without scheduling background work.
- Preserve the last known-good snapshot when research or validation fails.

## Non-Goals

- Do not rank Codex against Claude or recommend one provider over the other.
- Do not run calibration during every grill, seed, or packet generation.
- Do not create a cron job, scheduled task, startup hook, or automatic update.
- Do not rewrite existing issues when calibration changes.
- Do not guarantee that every model is available on every account or provider.
- Do not encode volatile model guidance directly in project profiles.
- Do not let a low-cost helper own a shipping lane by default.

## Approved Packet Contract

Future dispatchable packets contain a separate compact block:

```markdown
## Model routing

- Codex: <starting model> / <effort> → <escalation model> / <effort> if the packet's escalation condition triggers.
- Claude: <starting model> / <effort> → <escalation model> / <effort> if the packet's escalation condition triggers.
```

The arrow is optional. If the task already starts at the appropriate frontier
tier, or no useful escalation target exists, emit only the starting choice:

```markdown
## Model routing

- Codex: <model> / <effort>.
- Claude: <model> / <effort>.
```

For a non-dispatchable `owner` or `needs-grill` issue, use `Not applicable
until ratified` when no model-owned execution should begin. Do not invent an
implementation route simply to fill the block.

The block does not include calibration dates, rationale, model comparisons,
helper-agent policy, risk, or proof requirements. Those belong in the shared
snapshot or the packet's existing calibration fields.

### Illustrative ordinary packet

The following is an example, not fixed boilerplate:

```markdown
## Model routing

- Codex: Terra / Medium → Sol / High if the packet's escalation condition triggers.
- Claude: Sonnet 5 / High → Opus 4.8 / XHigh if the packet's escalation condition triggers.
```

The actual model and effort pair is selected anew for every packet.

## Architecture

### 1. Calibrator skill

Add a second Agent Skills-format skill inside this repository:

```text
calibrate-model-routing/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── scripts/
    └── calibration_snapshot.py
```

Its public invocation is `calibrate-model-routing`; clients may display it as
`/calibrate-model-routing` or `$calibrate-model-routing` according to their
skill UI.

The skill must:

1. Read the existing snapshot, if present.
2. Research the requested provider, or both providers by default.
3. Prefer official model-overview, model-selection, effort, and client
   configuration documentation.
4. Record model names, stable identifiers or aliases when useful, effort
   levels, defaults, official use cases, availability constraints, and source
   URLs.
5. Derive provider-local routing tiers without comparing providers.
6. Validate the complete proposed provider section.
7. Replace only the successfully calibrated provider section.
8. Show the user a concise before/after summary.

Use `scripts/calibration_snapshot.py` for structural validation and atomic
provider-section replacement. The script accepts a candidate provider section,
validates required headings and dates, writes through a temporary file, and
renames only after the full snapshot validates. This keeps partial refreshes
deterministic and preserves the untouched provider section byte-for-byte.

If official sources are inaccessible, contradictory, or incomplete, preserve
the last known-good provider section and report the uncertainty. Never replace
confirmed guidance with an unsupported guess.

The user can request a partial refresh, such as "calibrate Claude only." A
default invocation refreshes both providers.

### 2. Shared snapshot

Store the user-local snapshot at:

```text
~/.agents/model-routing/calibration.md
```

Allow `MODEL_ROUTING_CALIBRATION_PATH` to override that location for testing or
nonstandard setups. The neutral `~/.agents` location is shared by Codex and
Claude without making either tool the owner of the data.

The snapshot is Markdown with YAML frontmatter so it is human-readable and
easy for agents to parse. Each provider has its own `verified_at` date because
providers can be refreshed independently.

Required information:

```markdown
---
schema_version: 1
stale_after_days: 30
---

# Model routing calibration

## Codex

- Verified at: YYYY-MM-DD
- Official sources:
  - <URL>
- Client or account constraints:
- Workhorse:
- Frontier:
- Long-horizon or exceptional tier:
- Helper or high-volume tier:
- Effort guidance:
- Routing notes:

## Claude

...
```

The exact prose may evolve, but the headings and verification dates are the
schema contract. The snapshot contains volatile guidance; repository templates
contain only stable routing behavior.

### 3. Dispatch compiler integration

At the start of packet compilation, `dispatch-compiler` reads the snapshot and
the optional project profile.

Precedence is:

1. Current provider catalog and effort semantics from the shared snapshot.
2. Project constraints such as allowed models, unavailable tiers, mandatory
   review, or low-cost-lane restrictions.
3. Task-specific routing from the packet's evidence and calibration fields.

A project profile may narrow availability or require stronger review. It must
not silently redefine a model's current official role or compare providers.

If the snapshot is older than `stale_after_days`, continue using the last
known-good guidance and emit one non-blocking conversational reminder to run
`calibrate-model-routing`. Do not put the warning or date into the packet.

If the snapshot is missing or structurally invalid, compile the rest of the
packet but mark model routing as uncalibrated and tell the user how to run the
calibrator. Do not guess current model names.

## Task-Specific Routing

Routing uses information already present in the packet:

- dispatch status
- complexity
- risk and cost of being wrong
- ambiguity or product judgment
- autonomy and expected duration
- repetition or mechanical certainty
- proof and verification burden
- helper-agent policy
- escalation conditions

The compiler applies these rules separately to each provider:

1. Select the least expensive current tier that can safely own the work under
   the project policy.
2. Select effort based on how thoroughly the agent must inspect, execute, and
   verify the task. Effort is not merely task size.
3. Raise model capability when the problem is genuinely difficult, unfamiliar,
   ambiguous, or beyond the lower tier's knowledge.
4. Raise effort when failure would come from incomplete inspection, skipped
   tests, shallow verification, or stopping early.
5. Recommend a long-horizon specialist directly when the packet is already
   known to exceed an ordinary sitting. Do not make every packet climb through
   the full model ladder.
6. Add an escalation target only when a materially stronger, available route
   exists.
7. Point the arrow at the packet's existing escalation condition. Do not copy
   that condition into the model block.

Low-cost models remain appropriate for bounded evidence work, searches, log
reduction, screenshot inventory, duplicate detection, test running, and other
reviewable helper tasks. They do not own a shipping lane by default unless a
project profile explicitly permits it and the packet is mechanically certain.

## Current Claude Baseline

The initial snapshot should encode the official guidance verified during this
design:

- Sonnet 5 is the daily-coding workhorse and defaults to High effort.
- Opus 4.8 is the normal complex-reasoning and high-autonomy escalation; High
  is its default and XHigh is recommended for demanding coding and agentic
  work.
- Fable 5 is the most capable Claude Code model and is reserved for the hardest
  work or tasks larger than a single sitting. It is not the routine escalation
  on ordinary packets.
- Max effort is exceptional because it can have diminishing returns and
  overthink. It is not a generated default.

Initial official sources:

- <https://code.claude.com/docs/en/model-config>
- <https://platform.claude.com/docs/en/about-claude/models/overview>
- <https://platform.claude.com/docs/en/about-claude/models/choosing-a-model>
- <https://claude.com/blog/claude-model-and-effort-level-in-claude-code>

Codex guidance is populated by the first calibrator run from current official
OpenAI documentation rather than copied permanently into this design.

## Repository Changes During Implementation

Implementation should:

1. Add `calibrate-model-routing/` as a standalone nested skill.
2. Add and test the deterministic snapshot validation/update script.
3. Add installation instructions for symlinking the skill into Codex and
   Claude Code.
4. Update the root `dispatch-compiler` skill to read the shared snapshot.
5. Replace the two generic recommended-lane fields with the compact
   `## Model routing` block in templates and examples.
6. Update the project-profile template with availability and override fields.
7. Update the README to explain calibration versus per-packet routing.
8. Leave historical external issues and already-generated packets unchanged.

The implementation must not alter `homies-nextjs#166` or PR #170.

## Installation Contract

The source of truth remains this repository. Installation creates discoverable
links for both clients while both read the same snapshot:

```text
~/.codex/skills/calibrate-model-routing  -> <repo>/calibrate-model-routing
~/.claude/skills/calibrate-model-routing -> <repo>/calibrate-model-routing
```

The existing `dispatch-compiler` installation remains separate. Users may
install either skill independently, but automatic task routing requires both:
the calibrator produces the snapshot and the compiler consumes it.

## Failure and Safety Behavior

- Never erase a valid snapshot before the replacement validates.
- Never silently substitute third-party model rumors for official guidance.
- Never present provider availability as universal when it depends on account,
  client version, cloud provider, or organization policy.
- Never turn a stale reminder into an automatic browsing or writing action.
- Never block non-routing packet compilation because the snapshot is stale.
- Never compare Claude against Codex in a packet.
- Never expand the two-line packet block with the full calibration rationale.

## Verification Plan

Implementation is complete when all of the following pass:

1. The nested skill passes the skill creator's `quick_validate.py` check.
2. The snapshot helper's focused tests pass.
3. A first run with no snapshot creates a complete two-provider snapshot.
4. A Claude-only refresh preserves the Codex section byte-for-byte.
5. An official-source failure preserves the previous provider section.
6. A fresh snapshot produces no staleness warning.
7. A snapshot older than 30 days produces one non-blocking warning and still
   routes the packet.
8. A missing or invalid snapshot produces no guessed model names.
9. A routine implementation packet receives workhorse-to-frontier routing.
10. A bounded evidence-only packet can receive a helper-tier route.
11. A complex packet can start at a frontier tier without a redundant arrow.
12. A long-running Claude packet can select Fable directly.
13. An owner-only packet receives no implementation recommendation.
14. Codex and Claude recommendations are independent and contain no
    cross-provider preference.
15. Existing `dispatch-compiler` examples still demonstrate valid status,
    proof, and closeout behavior after migration.

Forward-testing with helper agents is optional and must follow the active
session's delegation policy. It is not required to validate the deterministic
snapshot and template behavior.

## Rollout

1. Land the implementation in `dispatch-compiler`.
2. Install both skills into Codex and Claude Code.
3. Run `calibrate-model-routing` once to create the initial snapshot.
4. Use the updated compiler for newly grilled or seeded packets.
5. Re-run calibration manually after provider announcements or when the stale
   reminder appears.

No scheduled task is created. The owner remains in control of when volatile
guidance is refreshed.
