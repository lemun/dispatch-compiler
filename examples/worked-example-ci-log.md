# Worked Example: One Flaky CI Log → Four Dispatchable Issues

The [first worked example](worked-example.md) starts from an owner complaint
and a live product walk. This one starts from the opposite corner: a raw CI
artifact, with **no runtime access at all** — the compile pass runs entirely
on logs and source. It shows the artifact-grounded evidence path, the
`blocked` label, and what "record what blocked live proof" looks like in
practice.

**The input.** A teammate drops this into the tracker:

> **#341 — Nightly E2E job is a coin flip**
>
> `e2e-nightly` has failed 6 of the last 14 runs. Different tests each time.
> People have started re-running until green. Log from last night attached:
> `run-4188.log`.

**The compile pass.** The agent running the skill:

1. Could not run the E2E suite locally — it requires a staging deployment the
   agent has no credentials for. Recorded that as the runtime blocker; all
   evidence below is artifact-grounded (the log) and code-grounded (the test
   source).
2. Clustered the 6 failing runs from CI history: 4 failures are one race in a
   shared polling helper; 2 are a `401` from the payments sandbox.
3. Found a third thing nobody asked about: the `screenshot-diff` suite has
   been red and `continue-on-error` for 11 weeks, silently masking whatever
   it once caught.
4. Filed four successor issues and closed #341 with a closeout comment.

The output, condensed (same template as the first example — full bodies
omitted where they'd repeat it):

---

## Successor issue 1 of 4

# Fix 2s hardcoded timeout race in `waitForToast` E2E helper

Labels: `ready`

## Charter

Source: #341. Expected outcome: `waitForToast` polls until timeout instead of
sleeping a fixed 2s, and the four affected specs stop flaking.

## Evidence

- Origin: artifact-grounded, code-grounded
- Confidence: high
- Evidence anchors:
  - Files: `e2e/helpers/toast.ts:17`
  - Commands: `grep -n "sleep(2000)" e2e/helpers/toast.ts`
  - Artifacts: `run-4188.log` lines 2210–2288; CI runs 4188, 4183, 4179, 4171
    all fail in specs that call `waitForToast` under load

Current behavior: helper does `sleep(2000)` then asserts the toast exists;
under a slow runner the toast renders at ~2.3s and the assertion fires early.

Expected behavior: poll with a 10s ceiling; assert on appearance, not on a
fixed delay.

Runtime proof status: **blocked** — suite needs staging credentials the lane
does not have. Substitute proof gate below runs the affected specs against
the mocked backend, which reproduces the race deterministically with an
artificial 2.5s render delay.

## Dispatch calibration

- Origin: artifact-grounded, code-grounded
- Confidence: high
- Complexity: S
- Risk: low (test-only change)
- Cost posture: frontier-reviewed helper lane
- Recommended Claude lane + effort: Sonnet-class lane, low effort
- Recommended Codex lane + effort: default lane, low effort
- Helper agents: allowed (log clustering already done; test running only)
- Parallel safety: file-disjoint from #343–#345
- Escalation triggers: fix requires touching specs outside the four callers
- Proof gate: `npm run e2e:mocked -- --grep @toast` passes 20/20 with injected 2.5s render delay

## Proof gate

- [ ] `npm run e2e:mocked -- --grep @toast` passes 20 consecutive runs with the injected delay.
- [ ] No remaining `sleep(` calls in `e2e/helpers/toast.ts`.

---

## Successor issue 2 of 4

# Re-enable checkout E2E specs once payments sandbox key is rotated

Labels: `blocked` (blocked by #345)

## Charter

Source: #341. Expected outcome: the two checkout specs run against a valid
sandbox key and are removed from the retry-until-green folklore.

## Evidence

- Origin: artifact-grounded
- Confidence: high
- Evidence anchors:
  - Artifacts: `run-4188.log` lines 3401–3419 —
    `POST https://sandbox.pay.example.com/v1/charges → 401 invalid_api_key`
  - Files: `e2e/checkout.spec.ts`, `.github/workflows/e2e-nightly.yml:44`
    (reads `PAY_SANDBOX_KEY` from repo secrets)

Current behavior: both checkout specs fail with `401 invalid_api_key` on
every run since run 4171 (June 22). This is not flake; it is a dead
credential presenting as flake.

Expected behavior: specs pass against a live sandbox key.

Runtime proof status: blocked — the credential itself is the blocker.

## Dispatch calibration

- Origin: artifact-grounded
- Confidence: high
- Complexity: S
- Risk: low
- Cost posture: frontier-reviewed helper lane
- Helper agents: allowed (CI run verification only)
- Parallel safety: sequenced after #345; file-disjoint from #342
- Escalation triggers: specs still fail after key rotation
- Proof gate: two consecutive green `e2e-nightly` runs with checkout specs enabled

The work is fully shaped — the only missing input is the rotated secret,
which is #345 and human-only. That is exactly what `blocked` is for: shaped
enough to dispatch the moment a named condition clears.

---

## Successor issue 3 of 4

# Decide fate of the screenshot-diff suite (red + ignored for 11 weeks)

Labels: `needs-grill`

## Charter

Source: surfaced while clustering #341 failures. Expected outcome: owner
picks one of three options so the suite stops being a silent no-op.

## Evidence

- Origin: autonomous, code-grounded
- Confidence: high (that the suite is dead weight), n/a (on what to do)
- Evidence anchors:
  - Files: `.github/workflows/e2e-nightly.yml:61` (`continue-on-error: true`
    added in commit `9f21c4a`, April 18)
  - Artifacts: last green `screenshot-diff` run is 4102 (April 17)

Options for the owner to ratify:

1. Fix the baselines and remove `continue-on-error` (est. M).
2. Delete the suite and rely on the component visual tests.
3. Keep it advisory but route failures to a dashboard instead of CI noise.

This is a judgment call about what the team wants from visual regression
coverage — not something an agent should decide by momentum.

## Dispatch calibration

- Origin: autonomous
- Confidence: high
- Complexity: n/a until ratified
- Risk: low
- Cost posture: n/a until ratified
- Helper agents: n/a
- Parallel safety: n/a (decision, not code)
- Proof gate: owner replies with a chosen option; issue relabeled `ready` with that spec

---

## Successor issue 4 of 4

# Rotate the payments sandbox API key in CI secrets

Labels: `owner`

## Charter

Source: #341 (root cause of the checkout failures). Expected outcome: a valid
`PAY_SANDBOX_KEY` in repo secrets.

Why this is `owner` and not `blocked`: rotating a payment-provider credential
requires vendor-dashboard access and secret-write permission that no agent
has or should have. #343 is the agent-shaped work that waits behind this.

## Evidence

- Origin: artifact-grounded
- Confidence: high
- Evidence anchors: `run-4188.log` lines 3401–3419; provider dashboard shows
  key age if the owner checks — agent could not verify expiry directly.

## Close criteria

- [ ] New key stored in repo secrets; old key revoked at the provider.

---

## The closeout comment posted on #341

# Dispatch Closeout

Source: #341 — "Nightly E2E job is a coin flip"

## Source disposition

- Final label state: none (compiled)
- Close state: closing
- Archive status: log analysis archived at `.context/dispatch/341/`
- Reason: fully consumed by successors #342–#345

## Successor issues

### Ready

- #342 — Fix 2s hardcoded timeout race in `waitForToast`

### Needs grill

- #344 — Decide fate of the screenshot-diff suite

### Blocked

- #343 — Re-enable checkout specs (blocked by #345)

### Owner

- #345 — Rotate the payments sandbox API key

## Dispatch now

- #342 — dispatchable immediately; mocked-backend proof gate does not need
  staging access.

## Waiting

- #343 — waits on #345 (human-only secret rotation).
- #344 — waits on owner choice among three named options.

## Deliberate non-items

- Did not file "make E2E suite faster": no evidence it is slow, only flaky.
- Did not file issues for the 2 runs that failed on runner-image pulls:
  infrastructure transient, 0 recurrences after June 25.

## Unresolved owner calls

- Screenshot-diff suite direction (#344).
- Sandbox key rotation (#345).

## Evidence inspected

- Live walk: **blocked** — no staging credentials in this lane; recorded on
  every successor.
- Code: `e2e/helpers/toast.ts`, `e2e/checkout.spec.ts`,
  `.github/workflows/e2e-nightly.yml`
- Artifacts: `run-4188.log`; CI history for runs 4102–4188
- Commands: log clustering script output archived

## Remaining risk

- Flake attribution is from 14 runs; if #342 lands and the failure rate does
  not drop to the two known credential failures, reopen investigation.

## Close action

- [x] Source issue has successor links.
- [x] Successors are grouped by status.
- [x] Source close reason is explicit.
- [x] No work remains in the source that a successor issue does not capture.

---

## What this example demonstrates that the first one doesn't

- **Runtime proof blocked, honestly.** Every issue names the blocker (no
  staging credentials) and the substitute evidence, instead of pretending
  the log alone equals a reproduction.
- **`blocked` vs `owner` in practice.** The checkout fix is agent-shaped
  work waiting on a named condition; the key rotation is the human-only
  condition itself. One label each, with the dependency edge written down.
- **Flake vs dead credential.** Clustering the log separated "6 flaky runs"
  into one real race and one expired secret — two different owners, two
  different fixes, instead of one doomed "fix flaky CI" ticket.
- **Silent failure surfaced.** Nobody asked about the screenshot-diff suite.
  A `continue-on-error` that has been red for 11 weeks is exactly the kind
  of finding that should become a crisp owner decision, not a unilateral
  agent cleanup.
