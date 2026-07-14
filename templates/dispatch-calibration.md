# Dispatch Calibration Block

Copy this block into every successor issue.

```markdown
## Dispatch calibration

- Origin: owner-ratified | live-walked | code-grounded | artifact-grounded | autonomous
- Confidence: high | medium | low
- Complexity: S | M | L | XL
- Risk: low | medium | high
- Cost posture: frontier-owned | frontier-reviewed helper lane | helper-only evidence pass
- Helper agents: allowed | limited | not allowed
- Parallel safety: file-disjoint | subsystem-disjoint | sequenced after #N | do not parallelize
- Escalation triggers:
- Proof gate:

## Model routing

- Codex:
- Claude:
```

## Field Guidance

`Origin` describes where the finding came from. Use more than one value when
needed.

`Confidence` describes certainty that the issue should exist, not certainty
that the implementation is easy.

`Complexity` estimates implementation size. Keep it rough.

`Risk` estimates the cost of a bad patch: data loss, payment flow breakage,
auth failure, release risk, user trust, or confusing product behavior.

`Cost posture` explains whether a frontier/senior agent should own the lane or
whether cheaper helpers may gather bounded evidence.

`Model routing` is generated per packet from the shared calibration snapshot,
project constraints, and this packet's traits. Name the starting model and
effort for each provider. Add an escalation target only when a materially
stronger route exists, and point to the packet's existing escalation condition
instead of repeating it. Do not rank providers.

`Helper agents` should be specific: search only, logs only, screenshot
inventory, duplicate scan, test runner, artifact extraction, or not allowed.

`Parallel safety` should name collisions and sequencing edges.

`Escalation triggers` are conditions that force the lane to stop and ask for
review.

`Proof gate` is the command, screenshot, manual path, test, or artifact check
that proves the issue is done.
