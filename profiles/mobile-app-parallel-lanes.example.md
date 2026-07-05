# Mobile App Parallel Lanes Dispatch Profile Example

This is an example of a project profile for a mobile product team running
parallel agent lanes through GitHub Issues, worktrees, and Conductor-style
queues. Treat the details as replaceable policy, not core `dispatch-compiler`
rules.

## Tracker

- Issue tracker: GitHub Issues.
- Core labels: `ready`, `needs-grill`, `blocked`, `owner`.
- Optional labels: `superseded`, `duplicate`, `wontfix`.
- Source review close policy: when a review or grill-style charter has emitted
  concrete successor issues, close the source with a seeded closeout comment.
- Superseded close policy: if current code or already-landed PRs fully consume
  the source charter, label it `superseded` and close with evidence links.
- PR close keyword policy: use `Closes #N` only when the PR fully completes the
  issue. Use `Refs #N` for partial work.

## Runtime Proof

- Runtime proof is preferred for product-surface, layout, onboarding,
  navigation, billing, auth, and settings findings.
- Each parallel lane owns its own checkout, dev server, simulator, emulator, or
  browser session. Do not reload, stop, or repurpose another lane's runtime.
- Store review evidence under a stable project path such as
  `.context/dispatch/<source-id>/`.
- If live runtime is blocked, pivot to code-path mapping plus artifact
  inspection. Record the blocker in the successor issue and closeout.
- Fresh workspaces may need dependency installation before tests or package
  inspection are trustworthy.

## Agent Lane Policy

- Default lane shape: one issue per worktree.
- Prefer file-disjoint lanes. If two issues touch the same screen, state the
  sequencing edge.
- Keep the source issue number visible in branch names, PR bodies, and closeout
  comments.
- For attached packet work, re-verify every bullet against current code before
  editing.
- Stage only intended files.
- PR body should start with:
  - What changed
  - Why
  - What to check

## Model Policy

- Shipping lane default: frontier or senior coding agent.
- Frontier review required for:
  - billing, auth, entitlement, data deletion, permissions, release, and
    navigation recovery
  - shared abstractions used by multiple surfaces
  - changes where product judgment is mixed with implementation
- Helper agents are allowed for:
  - screenshot inventory
  - log reduction
  - duplicate issue search
  - command/test running
  - code search and file mapping
- Helper agents are not allowed to own final product calls, risk acceptance, or
  merge-critical implementation without frontier review.
- No low-end model owns a shipping lane by default.

## Proof Gates

### Low risk

- Targeted unit test, lint, typecheck, or static inspection.
- Manual screenshot comparison when the issue is visual but simple.

### Medium risk

- Targeted test plus runtime walk of the affected surface.
- Screenshot or recording attached to the issue or PR.
- Explicit check for adjacent surfaces that share the same component.

### High risk

- Runtime walk on a lane-local simulator, emulator, browser, or dev server.
- Targeted tests plus any required build or prebuild command.
- Owner review if behavior touches billing, auth, permissions, release policy,
  user trust, or irreversible data.

## Escalation Triggers

- The current code does not match the source charter.
- Runtime proof fails for environmental reasons twice.
- The fix requires touching shared navigation, auth, billing, entitlement, or
  data mutation paths outside the issue scope.
- The implementation requires a product decision hidden inside the ticket.
- The lane cannot stay file-disjoint from another active lane.

## Closeout Rules

- Close a source review charter after successor issues are filed and linked.
- Leave it open if real product work remains unfiled.
- Mark it `superseded` when already-landed work consumes the charter.
- The closeout comment must group successors by label, separate dispatch-now
  from waiting, list deliberate non-items, name unresolved owner calls, and
  state final label/close/archive status.
