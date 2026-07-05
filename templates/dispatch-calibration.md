# Dispatch Calibration Block

Copy this block into every successor issue.

```markdown
## Dispatch calibration

- Origin: owner-ratified | live-walked | code-grounded | artifact-grounded | autonomous
- Confidence: high | medium | low
- Complexity: S | M | L | XL
- Risk: low | medium | high
- Cost posture: frontier-owned | frontier-reviewed helper lane | helper-only evidence pass
- Recommended Claude lane + effort:
- Recommended Codex lane + effort:
- Helper agents: allowed | limited | not allowed
- Parallel safety: file-disjoint | subsystem-disjoint | sequenced after #N | do not parallelize
- Escalation triggers:
- Proof gate:
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

`Recommended Claude lane + effort` and `Recommended Codex lane + effort` should
name the expected role and effort, not a universal winner.

`Helper agents` should be specific: search only, logs only, screenshot
inventory, duplicate scan, test runner, artifact extraction, or not allowed.

`Parallel safety` should name collisions and sequencing edges.

`Escalation triggers` are conditions that force the lane to stop and ask for
review.

`Proof gate` is the command, screenshot, manual path, test, or artifact check
that proves the issue is done.
