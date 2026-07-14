---
name: calibrate-model-routing
description: Refresh the shared Codex and Claude model-routing calibration from current official provider documentation. Use when the user explicitly asks to calibrate, refresh, or update model and effort recommendations, especially after OpenAI or Anthropic announces model, effort, alias, availability, or guidance changes.
---

# Calibrate Model Routing

Refresh volatile provider guidance without changing existing work packets.

## Scope

Refresh both providers unless the user names only Codex or only Claude. Keep
their recommendations independent. Never recommend one provider over another.

Resolve the snapshot path from `MODEL_ROUTING_CALIBRATION_PATH`; otherwise use
`~/.agents/model-routing/calibration.md`.

## Research

Use current official sources only.

- Codex: official `openai.com` and `chatgpt.com` documentation. Prefer the
  OpenAI documentation capability when the active client provides it.
- Claude: official `anthropic.com` and `claude.com` documentation, including
  Claude Code model configuration and Claude Platform model guidance.

For each requested provider, verify:

- current model names and stable IDs or aliases when useful
- client, account, plan, or cloud-provider availability constraints
- daily workhorse, frontier, long-horizon or exceptional, and helper tiers
- supported effort levels, defaults, and provider guidance
- whether increased model capability or increased effort addresses the failure
- all official source URLs used

If official sources conflict or do not support a complete provider section,
preserve the existing section and explain the uncertainty.

## Build the Candidate

Use this exact provider-section schema:

```markdown
## <Provider>

- Verified at: YYYY-MM-DD
- Official sources:
  - https://official.example/path
- Client or account constraints: <concise current constraint>
- Workhorse: <model, effort, and task fit>
- Frontier: <model, effort, and task fit>
- Long-horizon or exceptional tier: <model, effort, and task fit>
- Helper or high-volume tier: <model, effort, and task fit>
- Effort guidance: <when to raise or lower effort>
- Routing notes: <when to change models>
```

When creating the first snapshot, assemble both provider sections beneath:

```markdown
---
schema_version: 1
stale_after_days: 30
---

# Model routing calibration
```

Do not write model rumors, cross-provider rankings, packet examples, or long
rationales into the snapshot.

## Validate and Install

Resolve `scripts/calibration_snapshot.py` relative to this `SKILL.md`.

For a first or full refresh, save the candidate to a temporary file and run:

```bash
python3 scripts/calibration_snapshot.py install --input <candidate-file>
```

For a partial refresh, save the provider section to a temporary file and run:

```bash
python3 scripts/calibration_snapshot.py replace-provider \
  --provider codex|claude \
  --input <provider-section-file>
```

The helper validates official domains and writes atomically. If it rejects the
candidate, correct the evidence-backed defect or preserve the old snapshot.
Never weaken validation to force an update through.

## Report

Report:

- provider sections refreshed
- previous and new verification dates
- model or effort guidance that materially changed
- sections preserved because evidence was incomplete
- snapshot path

Do not modify existing packets, create a schedule, or start packet generation.
