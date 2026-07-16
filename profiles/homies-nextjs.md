# Homies Next.js Dispatch Profile

Use this profile only for the `homies-nextjs` marketing and waitlist site. The
repository's current `AGENTS.md` remains authoritative if this profile drifts.

## Tracker

- Issue tracker: GitHub Issues in `homies-nextjs`.
- Label set: `ready`, `needs-grill`, `blocked`, `superseded`, and `owner`.
- Leave unlabeled capture-inbox issues alone unless an owner-ratified session
  explicitly consumes them.
- Only owner-ratified sessions may apply `ready`. Autonomous sweeps and reviews
  use `needs-grill` or remain unlabeled; ease alone never makes work ready.
- `blocked` work names the blocking issue or exact condition. Confirm the
  blocker is still open before filing or dispatching it.
- `superseded` issues are not dispatchable. After posting the required final
  comment, close them when permissions allow.
- A dispatched implementation lane comments once with its branch name and does
  not edit the issue body, relabel it, or close it manually.
- PR close keyword policy: use `Closes #N` only when the merged PR fully
  completes the issue. Use `Refs #N` for partial work and name what remains.

## Runtime Proof

- Primary app entrypoint: run `npm run dev` and walk the affected browser route.
- Required local setup: run `npm install` in a fresh checkout.
- Required static gates: `npm run build`, plus the narrowest relevant checks.
- Required flow gate: run `npm run test:e2e` when the affected flow is covered
  or important enough to require browser automation.
- Product-surface proof should cover relevant desktop and mobile viewports, EN
  and HE when text or direction can change, and light and dark themes when
  styling can change.
- Store screenshots, recordings, research, and walk transcripts outside the
  repo unless they become durable product or implementation truth; link the
  exact artifact path from the packet.
- Mock production side effects for waitlist, email, support, referral, and
  Supabase flows unless the issue explicitly authorizes live operations.
- If runtime proof is blocked, use current code, tests, build output, and saved
  artifacts. Record the blocker and the exact substitute evidence.

## Agent Lane Policy

- Default lane shape: one issue, one worktree, one branch, and one PR.
- Branch naming: follow the active harness convention; Codex branches use the
  repository's `codex/` prefix.
- Re-verify every packet bullet against current code before editing. Skip and
  report stale findings instead of improvising beyond the named territory.
- Prefer file-disjoint lanes. Name sequencing edges when routes, locale files,
  shared components, tokens, or tests overlap.
- Keep each lane's dev server and browser state separate from other active
  lanes. Do not stop or repurpose another lane's runtime.
- Required PR body opening: What changed / Why it matters / What to check.
- UI changes include best-effort before and after proof in the relevant daily
  state.

## Model Policy

- Allowed Codex models: models available to the user and present in the shared
  calibration snapshot.
- Unavailable Codex tiers: any tier absent from the active account or snapshot.
- Allowed Claude models: models available to the user and present in the shared
  calibration snapshot.
- Unavailable Claude tiers: any tier absent from the active account or snapshot.
- Shipping lane default: choose the least expensive route that can safely own
  the packet; no low-cost helper owns a shipping lane by default.
- Senior or frontier review is mandatory for auth, privacy, data mutation,
  referral integrity, conversion-critical behavior, security, shared
  abstractions, or ambiguous cross-surface changes.
- Helper agents may inventory screenshots, search code, reduce logs, detect
  duplicates, run tests, or map files when the result is bounded and reviewed.
- Helper agents may not own product judgment, risk acceptance, or merge-critical
  implementation without the packet's required review.
- Low-cost shipping ownership: mechanically-certain only.
- Low-cost model stop conditions: scope drift, unclear copy or product intent,
  failing proof, RTL ambiguity, cross-surface impact, or shared-state changes.
- Do not rank providers: true.

## Proof Gates

### Low risk

- Targeted static inspection or test plus `npm run build` when build behavior
  can be affected.
- For simple copy, verify EN and HE parity and inspect the affected viewport.

### Medium risk

- Targeted tests, `npm run build`, and a runtime walk of the affected desktop
  and mobile surface.
- Capture light and dark or EN and HE evidence whenever the changed behavior
  varies across those states.

### High risk

- `npm run build`, relevant `npm run test:e2e` coverage, and runtime evidence
  for every affected locale, viewport, theme, and auth state.
- Use mocked or isolated external effects unless live operations are explicitly
  in scope and separately authorized.

## Escalation Triggers

- Current code contradicts the source charter or ratified evidence.
- The change expands into auth, privacy, security, referral integrity, data
  mutation, external delivery, or production configuration.
- EN/HE, desktop/mobile, light/dark, build, or browser proof fails.
- A supposedly isolated lane collides with another lane's files or runtime.
- The packet hides a product decision or cannot name an acceptable proof gate.

## Closeout Rules

- Close a source grill or review only after every remaining finding is captured
  by a successor or explicitly recorded as a deliberate non-item.
- Leave it open when real product work remains unfiled or an unresolved owner
  call still belongs to the charter.
- Mark it `superseded` and close when successor issues or already-landed work
  fully consume it.
- The final comment states grilling status and confidence, successors grouped
  by `ready` versus `needs-grill` and other labels, dispatch-now versus waiting,
  deliberate non-items, unresolved owner calls, evidence inspected, whether
  the source was closed, its final label state, and whether the Conductor
  session can be archived.
- If permissions prevent label or close actions, name the exact owner action
  that remains.
