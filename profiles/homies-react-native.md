# Homies React Native Dispatch Profile

Use this profile only for the `homies-react-native` Expo app. The repository's
current `AGENTS.md`, release docs, and safety contracts remain authoritative if
this profile drifts.

## Tracker

- Issue tracker: GitHub Issues in `homies-react-native`.
- Label set: `ready`, `needs-grill`, `blocked`, `superseded`, and `owner`.
- Leave unlabeled capture-inbox issues alone unless an owner-ratified session
  explicitly consumes them.
- Only owner-ratified sessions may apply `ready`. Autonomous sweeps and reviews
  use `needs-grill` or remain unlabeled; ease alone never makes work ready.
- `blocked` work begins with a named issue or exact condition. Recheck the
  blocker before dispatch.
- `superseded` issues are not dispatchable. Comment with exact successors or
  current evidence, then close when permissions allow.
- A dispatched implementation lane comments once with its branch name and does
  not edit the body, relabel, or close the issue manually.
- PR close keyword policy: use `Closes #N` only when the merged PR fully
  completes the issue. Use `Refs #N` for partial work and say what remains.
- Regressions receive a new issue; do not reopen a closed issue.

## Runtime Proof

- Required local setup: run `npm ci`; do not substitute `npm install` for a
  native or CI proof environment.
- Primary app entrypoint: run `npm run dev` for Metro and use `npm run ios` or
  the applicable dev client. Expo Go is unsupported.
- Required static gate: `npm run ci`, or a narrower gate only when the packet
  justifies why the untouched checks cannot be affected.
- Required runtime gate: `npm run e2e:smoke` for covered critical flows, plus a
  simulator or device walk for product, visual, or native behavior.
- Every concurrent lane owns a lane-local Metro port, worktree, dev client, and
  simulator or device. Keep the dev-client URL aligned with that lane's Metro.
  Never stop, reload, erase, or repurpose another lane's runtime.
- Product proof covers the affected platform, auth and onboarding state, EN and
  HE, RTL and dark mode, permissions, and native prompts when relevant.
- Every user-facing string requires locale parity proof.
- Native dependency, config plugin, SDK, permission, or generated-project work
  must satisfy the repository's prebuild/native verification and bump
  `app.json` `runtimeVersion` when the native runtime changes.
- Never touch production Supabase casually. Production migrations require the
  repository backup and migration workflow; never seed, reset, or hand-edit the
  production schema.
- Store screenshots, recordings, research, and walk transcripts outside the
  repo unless they become durable product truth; link exact artifact paths.
- When runtime proof is blocked, record the lane, command, device, and blocker,
  then use current code, tests, logs, or saved artifacts as the named fallback.

## Agent Lane Policy

- Default lane shape: one task gets one worktree and one branch, followed by one
  PR. Never commit to `main`.
- Branch naming: follow the active harness convention; Codex branches use the
  repository's `codex/` prefix.
- Give every worktree its own dependencies or the primary checkout's
  `node_modules`; never use a sibling lane's dependencies.
- Prefer file-disjoint work. Pause and coordinate before overlapping on a
  screen, migration, locale file, generated project, store document, or shared
  native configuration.
- Stage explicit paths only. Never use broad staging commands in a shared
  workspace.
- Re-verify every packet bullet against current code before editing. Skip and
  report stale findings instead of widening scope.
- Required PR body opening: What changed / Why it matters / What to check, plus
  best-effort before and after media for UI work.

## Model Policy

- Allowed Codex models: models available to the user and present in the shared
  calibration snapshot.
- Unavailable Codex tiers: any tier absent from the active account or snapshot.
- Allowed Claude models: models available to the user and present in the shared
  calibration snapshot.
- Unavailable Claude tiers: any tier absent from the active account or snapshot.
- Shipping lane default: choose the least expensive route that can safely own
  the packet; no low-cost helper owns a shipping lane by default.
- Senior or frontier review is mandatory for auth, entitlement, payments,
  privacy, data deletion, production data, permissions, navigation recovery,
  native configuration, release compatibility, shared abstractions, or unclear
  product judgment.
- Helper agents may inventory screenshots, search files, reduce logs, detect
  duplicate issues, run tests, or map platform differences when bounded and
  reviewed.
- Helper agents may not own product judgment, risk acceptance, production
  changes, release decisions, or merge-critical implementation without the
  packet's required review.
- Low-cost shipping ownership: mechanically-certain only.
- Low-cost model stop conditions: scope drift, shared state, failed runtime
  proof, platform divergence, RTL ambiguity, native changes, or unclear intent.
- Do not rank providers: true.

## Proof Gates

### Low risk

- Targeted test or static inspection, locale parity when strings change, and a
  runtime screenshot for visible behavior.

### Medium risk

- Relevant tests, justified CI coverage, and a lane-local simulator or device
  walk in affected locale, direction, theme, auth state, and platform.
- Use Maestro proof when the flow is covered and stable enough to automate.

### High risk

- `npm run ci`, applicable `npm run e2e:smoke` or targeted Maestro flow, and
  lane-local device proof.
- Native/config work also requires the repository's build or prebuild checks,
  runtime-version review, and release-document updates when applicable.
- Production data, billing, permissions, privacy, and release actions retain
  their explicit owner or manual gates.

## Escalation Triggers

- Current code, runtime, or release state contradicts the charter.
- Proof diverges by iOS versus Android, EN versus HE, LTR versus RTL, light
  versus dark, auth state, onboarding state, or entitlement state.
- A lane requires another lane's Metro, simulator, files, migration, locale
  data, native project, or shared configuration.
- Work expands into production data, billing, privacy, permissions, native
  configuration, runtime compatibility, store policy, or release operations.
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
