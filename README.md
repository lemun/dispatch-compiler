# dispatch-compiler

Compile fuzzy findings into proof-gated issues that parallel coding agents can
ship safely.

Works with **Claude Code, Codex, Cursor, and any agent that reads Markdown** —
it's an [Agent Skills](https://agentskills.io)–format skill plus plain-Markdown
templates. Tracker-agnostic: GitHub Issues, Linear, or a folder of files.

## The problem

Generation is cheap now. The bottleneck is everything around it: deciding what
should change, proving a finding is real before an agent spends an afternoon
on it, carving work so five parallel lanes merge cleanly, and verifying the
result. Most parallel-agent failures happen **before dispatch** — the task was
vague, too big, unverified, or secretly contained a product decision.

`dispatch-compiler` is the compile step between "something is off" and "an
agent can own this." It takes a messy input — an owner complaint, a review, a
research finding, a screenshot, a log — and lowers it into small,
evidence-backed, confidence-labeled issues with explicit proof gates and lane
boundaries. The name is literal: **dispatch** (work packets assignable to
agent lanes) + **compiler** (lower fuzzy input into typed, executable issues).

## Before and after

Input — a real-shaped owner issue:

> **#214 — Settings area feels off**
> Billing page took forever to load when I checked yesterday, and I'm pretty
> sure sign-out is broken from the settings screen. Also the whole settings
> area looks dated compared to the new dashboard. Can an agent clean this up?

Sent to an agent as-is, that becomes one giant unfocused PR plus a guess about
what "dated" means. Compiled, it becomes:

| Issue | Label | Why |
|---|---|---|
| Fix broken sign-out action | `ready` | Reproduced live, traced to a stale route constant, test named |
| Paginate invoice query (6.2s → <1.5s) | `ready` | Profiled, high-risk billing surface, frontier-owned lane |
| Decide visual direction for settings | `needs-grill` | "Looks dated" is taste — owner picks from 3 concrete options |
| Approve seeded-data policy for staging | `owner` | Data-governance call surfaced during profiling — human-only |

The two `ready` issues are file-disjoint and dispatch to parallel lanes today.
The restyle is explicitly sequenced after the pagination fix because both
touch the same page. The full pass — every issue body, calibration block, and
the closeout comment — is in
[examples/worked-example.md](examples/worked-example.md). A second example,
starting from a flaky CI log with no runtime access at all, is in
[examples/worked-example-ci-log.md](examples/worked-example-ci-log.md).

## Quick start

```bash
git clone https://github.com/lemun/dispatch-compiler.git
```

Install the compiler and optional calibrator for both harnesses. The helper is
safe to rerun: it accepts only an existing symlink with the exact intended
target and refuses every mismatch or non-symlink collision.

```bash
# Install all four skill links with collision checks
REPO_ROOT="$(pwd -P)/dispatch-compiler"

skill_sources=(
  "$REPO_ROOT"
  "$REPO_ROOT/calibrate-model-routing"
  "$REPO_ROOT"
  "$REPO_ROOT/calibrate-model-routing-claude"
)
skill_destinations=(
  "${CODEX_HOME:-$HOME/.codex}/skills/dispatch-compiler"
  "${CODEX_HOME:-$HOME/.codex}/skills/calibrate-model-routing"
  "$HOME/.claude/skills/dispatch-compiler"
  "$HOME/.claude/skills/calibrate-model-routing"
)

preflight_skill_links() {
  for source_path in "${skill_sources[@]}"; do
    if [ ! -e "$source_path" ]; then
      echo "Source does not exist: $source_path" >&2
      return 1
    fi
  done

  for index in "${!skill_destinations[@]}"; do
    source_path="${skill_sources[$index]}"
    destination_path="${skill_destinations[$index]}"
    if [ -L "$destination_path" ]; then
      existing_target="$(readlink "$destination_path")"
      if [ "$existing_target" != "$source_path" ]; then
        echo "Refusing to replace $destination_path: symlink targets $existing_target, expected $source_path" >&2
        return 1
      fi
    elif [ -e "$destination_path" ]; then
      echo "Refusing to replace $destination_path: path exists and is not a symlink" >&2
      return 1
    fi
  done
}

preflight_skill_links || exit 1

for index in "${!skill_destinations[@]}"; do
  destination_path="${skill_destinations[$index]}"
  if [ ! -L "$destination_path" ]; then
    mkdir -p "$(dirname "$destination_path")"
    ln -s "${skill_sources[$index]}" "$destination_path"
  fi
done
```

For another harness (Cursor, Gemini CLI, OpenCode, and similar), use its
skills directory or place `SKILL.md` in context and point the agent at
`templates/`.

Create the four labels in a target repo (skip if you use different names —
the workflow only needs the four states, not these exact strings):

```bash
gh label create ready       --description "Dispatchable by an agent now" --color 2ea44f
gh label create needs-grill --description "Real finding, awaiting owner judgment" --color f9d0c4
gh label create blocked     --description "Dispatchable once a named condition clears" --color d73a4a
gh label create owner       --description "Human-only action or decision" --color bfdadc
```

Then run it:

```text
Use the dispatch-compiler skill on GitHub issue #123.
Source repo: /path/to/repo.
Project profile: profiles/my-project.md if present.
Gather live evidence if practical. If runtime is blocked, use code-grounded or
artifact-grounded evidence and say what blocked runtime proof.
File successor issues directly and close out the source issue with the
closeout template.
```

## What a compiled issue contains

Every successor issue is built from
[templates/successor-issue.md](templates/successor-issue.md) and must carry:

- **Evidence with origin** — where the finding came from:
  `owner-ratified`, `live-walked` (observed in the running product),
  `code-grounded`, `artifact-grounded` (screenshot / log / recording), or
  `autonomous` (the agent inferred it — defaults to `needs-grill`).
- **Concrete anchors** — file paths, routes, UI strings, commands,
  screenshots. No anchor, no issue.
- **Scope boundaries** — in/out of scope, so the diff stays PR-sized.
- **A proof gate** — the command, test, screenshot, or manual walk that
  proves the work is done. This is the answer to "verification is the
  bottleneck": every issue ships with its own verification plan.
- **Parallel-safety notes** — file ownership, collision risk, and sequencing
  edges ("waits for #217"), so lanes stay one-file-one-owner.
- **A dispatch calibration block** ([template](templates/dispatch-calibration.md)):

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

- Codex:
- Claude:
```

Calibration is the cost-control mechanism, and it optimizes for **mergeable
output, not cheap model calls**. Risk is priced by the cost of a bad patch
(billing, auth, data), not diff size. Cheap models are great helpers for
bounded, reversible work — search, log reduction, screenshot inventory — but
no low-end model owns a shipping lane by default.

## The four states

- **`ready`** — an agent can start now. Reserved for owner-ratified findings
  or mechanically certain fixes with a concrete proof gate. Easy ≠ certain.
- **`needs-grill`** — the finding is real but the owner's judgment is
  missing. "Grill" as in interrogate: the owner gets a crisp decision to
  make, ideally with concrete options, instead of taste smuggled into a
  ready ticket.
- **`blocked`** — shaped enough to dispatch, but a *named* condition must
  clear first.
- **`owner`** — human-only: account access, billing choices, policy calls,
  data governance, release approval.

Keep the set this small. Agents route reliably over four states; they drift
over twelve.

## Where it sits in a parallel-agent stack

Worktree and lane tools — Conductor, vibe-kanban, uzi, claude-squad, or plain
`git worktree` — solve *isolation*: each agent gets its own checkout and
runtime. Your tracker holds the queue. `dispatch-compiler` is the step
upstream of both: it decides **what enters the queue and in what shape**, so
that what your lane tool executes is already small, evidenced, verifiable,
and collision-safe. It writes plain Markdown issues, so there is nothing to
integrate — if your lane tool can read an issue, it can consume compiled
output.

## Project profiles

The core workflow stays generic; project policy lives in a profile — required
test commands, runtime-proof rules, branch conventions, model routing,
lane-isolation rules, escalation triggers. Start from
[templates/project-profile.md](templates/project-profile.md); see a filled-in
example for a mobile team running Conductor-style worktree lanes at
[profiles/mobile-app-parallel-lanes.example.md](profiles/mobile-app-parallel-lanes.example.md).

Two built-in Homies profiles keep repository policy out of the generic skill:
[profiles/homies-nextjs.md](profiles/homies-nextjs.md) and
[profiles/homies-react-native.md](profiles/homies-react-native.md). The
compiler selects them only for those exact repository names unless the caller
supplies a profile explicitly.

## Companion grill front ends

The optional companion skills separate judgment from compilation:

- `grill-me` owns deliberation. It runs the one-decision-at-a-time interview
  and stops with a decision record unless the user explicitly asks to compile,
  dispatch, or file the result.
- `grill-walk` owns evidence collection and owner ratification across a live
  artifact or code-grounded fallback. It emits a structured handoff, then must
  invoke `dispatch-compiler` for lane carving, packet schema, model routing,
  tracker mutation, and closeout.

Install their single versioned source for both Codex and Claude:

```bash
bash scripts/install-grill-frontends.sh
```

The installer creates direct links under `~/.agents/skills` and
`~/.claude/skills`, is safe to rerun, and refuses all collisions before making
changes. It also refuses stale same-named copies under
`${CODEX_HOME:-$HOME/.codex}/skills`, because duplicate discovery entries can
drift or both appear in a picker. Back up and remove any legacy copies first,
then rerun the installer. Restart the client if an updated skill does not
appear immediately.

## Model routing calibration

Model guidance changes faster than issue templates. Run
`$calibrate-model-routing` manually after OpenAI or Anthropic announces a
relevant model, effort, alias, availability, or guidance change, or when the
compiler reports that the 30-day snapshot is stale.

The calibrator writes `~/.agents/model-routing/calibration.md`. The compiler
then routes every new packet independently from that snapshot, the project
profile, and the packet's complexity, risk, ambiguity, autonomy, and proof
burden. Packets receive two compact lines: one for Codex users and one for
Claude users. Neither line recommends a provider over the other.

Calibration is never scheduled, never runs during every grill, and never
rewrites existing packets.

## Closeout discipline

A source issue doesn't just get closed — it ends with a dispatch ledger
([template](templates/source-closeout-comment.md)): successors grouped by
label, dispatch-now vs waiting, deliberate non-items, unresolved owner calls,
and evidence inspected. Deliberate non-items matter most: writing down what
you chose *not* to file is what keeps agent-generated backlogs from silting
up.

The skill also has explicit **stop conditions**: when code contradicts the
charter, evidence can't be anchored, the proof gate can't run, or lanes can't
be made collision-safe, the agent stops and reports instead of manufacturing
confidence.

## Repo structure

```text
dispatch-compiler/
├── SKILL.md                    # the agent workflow (Agent Skills format)
├── grill-me/SKILL.md           # deliberation wrapper; dispatch is opt-in
├── grill-me-claude/            # Claude manual-only entrypoint
│   ├── SKILL.md
│   └── WORKFLOW.md -> ../grill-me/SKILL.md
├── grill-walk/SKILL.md         # evidence and ratification front end
├── scripts/
│   └── install-grill-frontends.sh
├── templates/
│   ├── successor-issue.md
│   ├── dispatch-calibration.md
│   ├── source-closeout-comment.md
│   └── project-profile.md
├── profiles/
│   ├── homies-nextjs.md
│   ├── homies-react-native.md
│   └── mobile-app-parallel-lanes.example.md
├── examples/
│   ├── worked-example.md        # fuzzy owner complaint → four issues + closeout
│   └── worked-example-ci-log.md # flaky CI log, runtime blocked → four issues
└── LICENSE
```

## What this does not do

- It does not choose a provider for the user or refresh model guidance without
  an explicit calibration run.
- It does not replace owner judgment.
- It does not guarantee that parallel lanes will merge cleanly.
- It does not turn weak evidence into ready work.

It gives agents a sharper contract: inspect current state, produce concrete
evidence, route uncertainty honestly, and leave the board cleaner than you
found it.

## License

[MIT](LICENSE)
