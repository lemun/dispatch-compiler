# Worked Example: One Fuzzy Complaint → Four Dispatchable Issues

This is a complete, realistic pass through the dispatch-compiler loop. Names
and paths are fictional but the shape is exactly what the workflow produces.

**The input.** The owner of a SaaS web app files this issue:

> **#214 — Settings area feels off**
>
> Billing page took forever to load when I checked yesterday, and I'm pretty
> sure sign-out is broken from the settings screen. Also the whole settings
> area looks dated compared to the new dashboard. Can an agent clean this up?

This is a classic un-dispatchable issue: three unrelated problems, one
verified by nobody, mixed with a product-taste judgment. Sending it to a
coding agent as-is produces a giant unfocused PR or a wrong guess about what
"dated" means.

**The compile pass.** The agent running the skill:

1. Walked the live app (staging), reproduced what it could, captured
   screenshots to `.context/dispatch/214/`.
2. Confirmed sign-out fails with a console error; traced it to a stale route
   constant in code. Mechanically certain.
3. Measured billing page load: 6.2s, caused by an unpaginated invoice query.
   Real, but the fix touches a shared data layer.
4. Could not act on "looks dated" — that is product taste the owner never
   specified.
5. Filed four successor issues, carved into safe lanes, and closed #214 with
   a closeout comment.

The rest of this file is the actual output.

---

## Successor issue 1 of 4

# Fix broken sign-out action on settings screen

Labels: `ready`

## Charter

Source: #214 (owner complaint, confirmed by live walk)

Expected outcome: Clicking "Sign out" on `/settings/account` ends the session
and redirects to `/login`.

Why this matters: Users cannot end their session from settings; support has
two matching complaints.

## Evidence

- Origin: live-walked, code-grounded
- Confidence: high
- Evidence anchors:
  - Files: `src/features/settings/AccountPanel.tsx:88`, `src/routes.ts:41`
  - Routes or surfaces: `/settings/account`
  - UI strings: "Sign out"
  - Commands: `npm test -- AccountPanel`
  - Screenshots, recordings, logs, or artifacts:
    `.context/dispatch/214/signout-console-error.png`

Current behavior: Click fires `POST /api/auth/logout/` (trailing slash), API
returns 404, session persists, no user feedback. Console:
`POST http://localhost:3000/api/auth/logout/ 404`.

Expected behavior: Session cleared, redirect to `/login`.

Runtime proof status: Reproduced on staging, 2026-07-05.

## Scope

In scope:

- Fix the logout route constant in `src/routes.ts`.
- Add a regression test for the sign-out action.

Out of scope:

- Any visual changes to the settings screen (see #218).
- Auth token lifetimes or session policy.

## Implementation notes

- `src/routes.ts:41` defines `LOGOUT: '/api/auth/logout/'`; the API router in
  `server/api/auth.ts` registers `/api/auth/logout` (no trailing slash).

## Dispatch calibration

- Origin: live-walked, code-grounded
- Confidence: high
- Complexity: S
- Risk: medium (auth-adjacent, but the change is a one-line constant + test)
- Cost posture: frontier-reviewed helper lane
- Helper agents: allowed (test running only)
- Parallel safety: file-disjoint from #217 and #218
- Escalation triggers: fix requires touching session middleware or token logic
- Proof gate: `npm test -- AccountPanel` passes; manual sign-out on staging redirects to `/login`

The model names below illustrate the calibration current when this example was
written; generated packets use the shared snapshot instead of copying them.

## Model routing

- Codex: Terra / Medium → Sol / High if the packet's escalation condition triggers.
- Claude: Sonnet 5 / High → Opus 4.8 / XHigh if the packet's escalation condition triggers.

## Parallelization

Can run in parallel with: #217, #218

Must wait for: nothing

Likely file ownership: `src/routes.ts`, `src/features/settings/AccountPanel.tsx`

Collision risk: low — no other open lane touches these files

## Proof gate

- [ ] `npm test -- AccountPanel` passes with a new regression test.
- [ ] Manual sign-out on staging ends the session and redirects to `/login`.

## Close criteria

- [ ] Implementation matches expected behavior.
- [ ] Proof gate is satisfied or the issue comment names the verification blocker.
- [ ] PR uses `Closes #216` only if this issue is fully resolved.

## Escalation triggers

- The fix turns out to require changes to session middleware or auth tokens.

---

## Successor issue 2 of 4

# Paginate invoice query behind billing page load

Labels: `ready`

## Charter

Source: #214 (owner complaint, confirmed by live walk + profiling)

Expected outcome: `/settings/billing` loads in under 1.5s for accounts with
large invoice histories.

Why this matters: 6.2s measured load on a 400-invoice account; the query cost
grows linearly with account age, so this gets worse for exactly the customers
who pay the most.

## Evidence

- Origin: live-walked, code-grounded
- Confidence: high
- Evidence anchors:
  - Files: `server/api/billing.ts:112`, `src/features/billing/InvoiceList.tsx`
  - Routes or surfaces: `/settings/billing`, `GET /api/billing/invoices`
  - Commands: `npm run profile -- /settings/billing`
  - Screenshots, recordings, logs, or artifacts:
    `.context/dispatch/214/billing-waterfall.png`

Current behavior: `GET /api/billing/invoices` returns every invoice with full
line items; 5.8s of the 6.2s load is this one request.

Expected behavior: Paginated endpoint (25 per page), list renders on first
page of results.

Runtime proof status: Profiled on staging with a seeded 400-invoice account,
2026-07-05.

## Scope

In scope:

- Add pagination to the invoices endpoint and consume it in `InvoiceList`.

Out of scope:

- Redesign of the billing page (see #218).
- Invoice PDF generation performance.

## Implementation notes

- The endpoint is also consumed by the admin export at
  `server/api/admin/export.ts` — keep an unpaginated internal path or update
  the export caller.

## Dispatch calibration

- Origin: live-walked, code-grounded
- Confidence: high
- Complexity: M
- Risk: high (billing surface; a bad patch hides invoices from customers)
- Cost posture: frontier-owned
- Helper agents: limited (profiling runs and log reduction only)
- Parallel safety: subsystem-disjoint from #216; shares `/settings/billing` surface with #218 — sequenced before #218
- Escalation triggers: pagination requires schema changes, or the admin export cannot be kept correct
- Proof gate: profile shows <1.5s load on the seeded account; invoice count on final page matches DB count

## Model routing

- Codex: Sol / High.
- Claude: Opus 4.8 / XHigh.

## Parallelization

Can run in parallel with: #216

Must wait for: nothing

Likely file ownership: `server/api/billing.ts`, `src/features/billing/InvoiceList.tsx`

Collision risk: #218 will restyle the same page — #218 is sequenced after this issue.

## Proof gate

- [ ] `npm run profile -- /settings/billing` shows <1.5s on the 400-invoice seed account.
- [ ] Total invoice count across pages equals the DB count for the seed account.
- [ ] Admin export still produces a complete CSV.

## Close criteria

- [ ] Implementation matches expected behavior.
- [ ] Proof gate is satisfied or the issue comment names the verification blocker.
- [ ] PR uses `Closes #217` only if this issue is fully resolved.

## Escalation triggers

- Pagination requires a schema migration.
- The admin export path cannot be verified.

---

## Successor issue 3 of 4

# Decide the visual direction for the settings area

Labels: `needs-grill`

## Charter

Source: #214 ("the whole settings area looks dated compared to the new
dashboard")

Expected outcome: Owner picks a direction so a restyle lane can be dispatched
with a concrete target.

Why this matters: "Looks dated" is real feedback but not a spec. An agent
guessing at taste produces churn.

## Evidence

- Origin: autonomous (the specific gaps below are the agent's reading of the
  owner's one-line complaint)
- Confidence: medium
- Evidence anchors:
  - Routes or surfaces: `/settings/*` vs `/dashboard`
  - Screenshots, recordings, logs, or artifacts:
    `.context/dispatch/214/settings-vs-dashboard.png` (side-by-side)

Current behavior: Settings uses the pre-2025 component set (`LegacyCard`,
`LegacyTabs`); dashboard uses the new `ui/` kit with different spacing,
radius, and type scale.

Expected behavior: Unknown — candidate directions for the owner to ratify:

1. Mechanical swap to the new `ui/` kit, same layout.
2. Swap plus layout consolidation (merge Account + Profile tabs).
3. Leave as-is until the design refresh project covers it.

Runtime proof status: Side-by-side screenshots captured on staging.

## Dispatch calibration

- Origin: autonomous
- Confidence: medium
- Complexity: M (for option 1) — unknown for option 2
- Risk: low
- Cost posture: frontier-reviewed helper lane (once ratified)
- Helper agents: allowed (screenshot inventory already done)
- Parallel safety: touches `/settings/*` surfaces — must be sequenced after #217
- Escalation triggers: n/a — this issue is a decision request
- Proof gate: owner replies with a chosen direction; issue is then relabeled `ready` with a concrete spec

## Model routing

- Codex: Not applicable until ratified.
- Claude: Not applicable until ratified.

## Parallelization

Can run in parallel with: n/a (decision, not code)

Must wait for: owner input; any resulting restyle lane waits for #217

## Close criteria

- [ ] Owner has ratified one direction (or explicitly deferred).
- [ ] A `ready` successor exists with the chosen spec, or this is closed as deferred.

---

## Successor issue 4 of 4

# Approve seeded-data policy for staging profiling accounts

Labels: `owner`

## Charter

Source: #214 (surfaced while profiling billing)

Expected outcome: Owner decides whether the seeded 400-invoice account (built
from an anonymized production snapshot) may stay on staging permanently.

Why this matters: #217's proof gate depends on this account. Data policy for
anything derived from production is a human call, not an agent call.

## Evidence

- Origin: autonomous
- Confidence: high (that the decision is needed)
- Evidence anchors:
  - Commands: `npm run seed -- --profile billing-heavy`
  - Screenshots, recordings, logs, or artifacts: seed script at `scripts/seed-billing-heavy.ts`

## Dispatch calibration

- Origin: autonomous
- Confidence: high
- Complexity: S
- Risk: medium (data governance)
- Cost posture: n/a — human-only
- Helper agents: not allowed
- Parallel safety: n/a
- Proof gate: owner comment approving or rejecting the policy

## Model routing

- Codex: Not applicable until ratified.
- Claude: Not applicable until ratified.

## Close criteria

- [ ] Owner has approved, rejected, or replaced the seeding approach.

---

## The closeout comment posted on #214

# Dispatch Closeout

Source: #214 — "Settings area feels off"

## Source disposition

- Final label state: none (plain issue, now compiled)
- Close state: closing
- Archive status: evidence archived at `.context/dispatch/214/`
- Reason: fully consumed by successor issues #216–#219

## Successor issues

### Ready

- #216 — Fix broken sign-out action on settings screen
- #217 — Paginate invoice query behind billing page load

### Needs grill

- #218 — Decide the visual direction for the settings area

### Blocked

- (none)

### Owner

- #219 — Approve seeded-data policy for staging profiling accounts

## Dispatch now

- #216 and #217 — file-disjoint, can run as parallel lanes today.

## Waiting

- #218 — waiting on owner direction; any restyle lane is sequenced after #217
  because both touch `/settings/billing`.
- #219 — human-only decision; #217's proof gate is runnable meanwhile, but the
  seed account's long-term status is unresolved.

## Deliberate non-items

- Did not file anything for the settings page's slow tab-switch animation:
  measured at 180ms, within normal range; owner did not mention it.
- Did not file a general "audit settings accessibility" issue: no evidence
  gathered; would be a speculative ticket.

## Unresolved owner calls

- Visual direction for settings (#218).
- Seeded-data policy (#219).

## Evidence inspected

- Live walk: staging, all `/settings/*` routes, 2026-07-05
- Code: `src/routes.ts`, `src/features/settings/`, `server/api/billing.ts`
- Commands: `npm test -- AccountPanel`, `npm run profile -- /settings/billing`
- Screenshots or recordings: 3 files under `.context/dispatch/214/`

## Remaining risk

- The billing pagination lane (#217) touches a shared endpoint; its proof gate
  includes the admin export for that reason.

## Close action

- [x] Source issue has successor links.
- [x] Successors are grouped by status.
- [x] Source close reason is explicit.
- [x] No work remains in the source that a successor issue does not capture.

---

## Why this beats dispatching #214 directly

- The sign-out fix ships today from a cheap lane with a real proof gate,
  instead of being buried inside a restyle PR.
- The billing fix is correctly flagged as high-risk and frontier-owned, with
  the shared admin-export path caught **before** an agent broke it.
- The taste question goes to the owner as a crisp A/B/C decision instead of an
  agent guessing.
- The data-policy question — which nobody asked — got surfaced instead of
  silently becoming precedent.
- Two lanes run in parallel with zero file overlap, and the sequencing edge
  (#218 after #217) is written down where the next agent will see it.
