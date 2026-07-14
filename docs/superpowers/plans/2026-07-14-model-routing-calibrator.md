# Model Routing Calibrator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an on-demand calibration skill that maintains current official Codex and Claude model guidance, then make `dispatch-compiler` generate compact task-specific routing for new packets.

**Architecture:** A dependency-free Python helper validates and atomically updates a shared Markdown snapshot at `~/.agents/model-routing/calibration.md`. The new `calibrate-model-routing` skill researches official provider documentation and writes through that helper; the existing `dispatch-compiler` skill consumes the snapshot, project constraints, and packet traits to emit one independent routing line per provider.

**Tech Stack:** Agent Skills Markdown, Python 3 standard library, `unittest`, YAML UI metadata, Git

## Global Constraints

- Calibration is manually invoked and is never scheduled or triggered automatically.
- Use official OpenAI and Anthropic sources by default; preserve the last known-good provider section when official guidance is incomplete.
- Keep Codex and Claude recommendations independent; never recommend one provider over the other.
- Store the shared snapshot at `~/.agents/model-routing/calibration.md`, overridable with `MODEL_ROUTING_CALIBRATION_PATH`.
- Treat a provider section as stale after 30 days, continue routing from it, and warn conversationally without adding the date or warning to packets.
- Never rewrite already-generated packets.
- Keep packet output to `## Model routing` plus one compact line per provider.
- Do not allow low-cost helpers to own shipping lanes by default.
- Do not touch `homies-nextjs#166` or PR #170.
- Use no runtime dependency beyond Python 3's standard library.

---

## File Map

- `calibrate-model-routing/SKILL.md`: manual official-source research and snapshot update workflow.
- `calibrate-model-routing/agents/openai.yaml`: Codex UI metadata; implicit invocation disabled.
- `calibrate-model-routing/scripts/calibration_snapshot.py`: validate, install, replace, and report snapshot freshness atomically.
- `tests/test_calibration_snapshot.py`: focused behavior tests for snapshot validation, replacement, and staleness.
- `tests/test_markdown_contract.py`: repository-level contract tests for the compact routing block and stale-snapshot behavior.
- `SKILL.md`: consume the snapshot and route each packet independently.
- `templates/dispatch-calibration.md`: stable calibration fields plus compact routing contract.
- `templates/successor-issue.md`: issue skeleton with separate routing block.
- `templates/project-profile.md`: provider availability and low-cost ownership constraints.
- `examples/worked-example.md`: migrated live-evidence examples.
- `examples/worked-example-ci-log.md`: migrated artifact-evidence examples.
- `README.md`: installation, calibration, routing, and failure behavior.

### Task 1: Scaffold the Skill and Build the Snapshot Helper

**Files:**
- Create: `calibrate-model-routing/SKILL.md`
- Create: `calibrate-model-routing/agents/openai.yaml`
- Create: `calibrate-model-routing/scripts/calibration_snapshot.py`
- Create: `tests/test_calibration_snapshot.py`

**Interfaces:**
- Produces: `validate_snapshot(text: str) -> None`
- Produces: `validate_provider_section(provider: str, section: str) -> None`
- Produces: `replace_provider(snapshot: str, provider: str, section: str) -> str`
- Produces: `stale_providers(snapshot: str, today: date | None = None) -> list[str]`
- Produces CLI: `validate`, `install`, `replace-provider`, and `status`

- [ ] **Step 1: Initialize the nested skill with the official scaffold**

Run:

```bash
python3 /Users/shai/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  calibrate-model-routing \
  --path . \
  --resources scripts \
  --interface display_name="Calibrate Model Routing" \
  --interface short_description="Refresh Codex and Claude model routing guidance" \
  --interface default_prompt='Use $calibrate-model-routing to refresh shared model and effort guidance from official sources.'
```

Expected: `calibrate-model-routing/` contains `SKILL.md`, `agents/openai.yaml`, and `scripts/`.

- [ ] **Step 2: Write failing snapshot tests**

Create `tests/test_calibration_snapshot.py`:

```python
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "calibrate-model-routing" / "scripts" / "calibration_snapshot.py"
SPEC = importlib.util.spec_from_file_location("calibration_snapshot", SCRIPT)
assert SPEC and SPEC.loader
snapshot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(snapshot)


CODEX = """## Codex

- Verified at: 2026-07-14
- Official sources:
  - https://developers.openai.com/api/docs/guides/latest-model
- Client or account constraints: Availability depends on the active Codex client and plan.
- Workhorse: Terra / Medium for ordinary implementation.
- Frontier: Sol / High for complex or high-value work.
- Long-horizon or exceptional tier: Sol / Extra High only when current official guidance supports it.
- Helper or high-volume tier: Luna / Low for bounded reviewable work.
- Effort guidance: Raise effort when inspection or verification is incomplete.
- Routing notes: Increase model capability when the task exceeds the lower tier's knowledge.
"""

CLAUDE = """## Claude

- Verified at: 2026-07-14
- Official sources:
  - https://code.claude.com/docs/en/model-config
- Client or account constraints: Aliases and availability vary by provider and account.
- Workhorse: Sonnet 5 / High for daily coding.
- Frontier: Opus 4.8 / XHigh for complex coding and high-autonomy work.
- Long-horizon or exceptional tier: Fable 5 / High for work larger than a single sitting.
- Helper or high-volume tier: Haiku 4.5 / Default for bounded high-volume work.
- Effort guidance: Raise effort when Claude skips files, tests, or verification.
- Routing notes: Raise model capability when Claude tries fully but lacks capability.
"""


def full_snapshot(codex: str = CODEX, claude: str = CLAUDE) -> str:
    return """---
schema_version: 1
stale_after_days: 30
---

# Model routing calibration

""" + codex.rstrip() + "\n\n" + claude.rstrip() + "\n"


class SnapshotTests(unittest.TestCase):
    def test_valid_snapshot_passes(self) -> None:
        snapshot.validate_snapshot(full_snapshot())

    def test_rejects_nonofficial_provider_source(self) -> None:
        bad = CLAUDE.replace("https://code.claude.com", "https://example.com")
        with self.assertRaisesRegex(snapshot.SnapshotError, "official Claude domain"):
            snapshot.validate_snapshot(full_snapshot(claude=bad))

    def test_claude_replacement_preserves_codex_bytes(self) -> None:
        original = full_snapshot()
        replacement = CLAUDE.replace("2026-07-14", "2026-07-15")
        updated = snapshot.replace_provider(original, "claude", replacement)
        original_prefix = original[: original.index("## Claude")]
        updated_prefix = updated[: updated.index("## Claude")]
        self.assertEqual(original_prefix, updated_prefix)
        self.assertIn("- Verified at: 2026-07-15", updated)

    def test_staleness_is_computed_per_provider(self) -> None:
        codex = CODEX.replace("2026-07-14", "2026-05-01")
        self.assertEqual(
            snapshot.stale_providers(full_snapshot(codex=codex), date(2026, 7, 14)),
            ["codex"],
        )

    def test_atomic_install_creates_parent_and_valid_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "nested" / "calibration.md"
            snapshot.atomic_install(target, full_snapshot())
            self.assertEqual(target.read_text(), full_snapshot())
            snapshot.validate_snapshot(target.read_text())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the tests to verify they fail**

Run:

```bash
python3 -m unittest tests/test_calibration_snapshot.py -v
```

Expected: FAIL because `calibration_snapshot.py` does not yet define the tested interface.

- [ ] **Step 4: Implement the dependency-free snapshot helper**

Create `calibrate-model-routing/scripts/calibration_snapshot.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_PATH = Path("~/.agents/model-routing/calibration.md").expanduser()
PROVIDERS = {"codex": "Codex", "claude": "Claude"}
OFFICIAL_DOMAINS = {
    "codex": ("openai.com", "chatgpt.com"),
    "claude": ("anthropic.com", "claude.com"),
}
REQUIRED_FIELDS = (
    "Verified at",
    "Official sources",
    "Client or account constraints",
    "Workhorse",
    "Frontier",
    "Long-horizon or exceptional tier",
    "Helper or high-volume tier",
    "Effort guidance",
    "Routing notes",
)


class SnapshotError(ValueError):
    pass


def target_path(value: str | None = None) -> Path:
    configured = value or os.environ.get("MODEL_ROUTING_CALIBRATION_PATH")
    return Path(configured).expanduser() if configured else DEFAULT_PATH


def _frontmatter(snapshot: str) -> dict[str, str]:
    match = re.match(r"\A---\n(?P<body>.*?)\n---\n", snapshot, re.DOTALL)
    if not match:
        raise SnapshotError("snapshot must start with YAML frontmatter")
    fields: dict[str, str] = {}
    for line in match.group("body").splitlines():
        if ":" not in line:
            raise SnapshotError(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    if fields.get("schema_version") != "1":
        raise SnapshotError("schema_version must be 1")
    try:
        if int(fields.get("stale_after_days", "0")) <= 0:
            raise ValueError
    except ValueError as error:
        raise SnapshotError("stale_after_days must be a positive integer") from error
    return fields


def _section_bounds(snapshot: str, provider: str) -> tuple[int, int]:
    display = PROVIDERS[provider]
    heading = f"## {display}\n"
    start = snapshot.find(heading)
    if start < 0:
        raise SnapshotError(f"missing {display} section")
    later = [
        snapshot.find(f"## {other}\n", start + len(heading))
        for key, other in PROVIDERS.items()
        if key != provider
    ]
    ends = [position for position in later if position >= 0]
    return start, min(ends) if ends else len(snapshot)


def provider_section(snapshot: str, provider: str) -> str:
    start, end = _section_bounds(snapshot, provider)
    return snapshot[start:end].rstrip() + "\n"


def _provider_date(section: str) -> date:
    match = re.search(r"(?m)^- Verified at: (\d{4}-\d{2}-\d{2})$", section)
    if not match:
        raise SnapshotError("provider section needs an ISO Verified at date")
    try:
        return date.fromisoformat(match.group(1))
    except ValueError as error:
        raise SnapshotError("Verified at must be a valid ISO date") from error


def validate_provider_section(provider: str, section: str) -> None:
    if provider not in PROVIDERS:
        raise SnapshotError(f"unknown provider: {provider}")
    display = PROVIDERS[provider]
    if not section.startswith(f"## {display}\n"):
        raise SnapshotError(f"section must start with ## {display}")
    for field in REQUIRED_FIELDS:
        if not re.search(rf"(?m)^- {re.escape(field)}:", section):
            raise SnapshotError(f"{display} section missing {field}")
    _provider_date(section)
    urls = re.findall(r"https://[^\s>]+", section)
    if not urls:
        raise SnapshotError(f"{display} section needs an official source URL")
    allowed = OFFICIAL_DOMAINS[provider]
    for url in urls:
        host = (urlparse(url).hostname or "").lower()
        if not any(host == domain or host.endswith(f".{domain}") for domain in allowed):
            raise SnapshotError(f"source must use an official {display} domain: {url}")


def validate_snapshot(snapshot: str) -> None:
    _frontmatter(snapshot)
    if "# Model routing calibration\n" not in snapshot:
        raise SnapshotError("snapshot needs the model routing calibration title")
    codex_start, _ = _section_bounds(snapshot, "codex")
    claude_start, _ = _section_bounds(snapshot, "claude")
    if codex_start >= claude_start:
        raise SnapshotError("Codex section must precede Claude section")
    for provider in PROVIDERS:
        validate_provider_section(provider, provider_section(snapshot, provider))


def replace_provider(snapshot: str, provider: str, section: str) -> str:
    validate_snapshot(snapshot)
    normalized = section.rstrip() + "\n"
    validate_provider_section(provider, normalized)
    start, end = _section_bounds(snapshot, provider)
    separator = "\n" if end < len(snapshot) else ""
    updated = snapshot[:start] + normalized + separator + snapshot[end:]
    validate_snapshot(updated)
    return updated


def stale_providers(snapshot: str, today: date | None = None) -> list[str]:
    fields = _frontmatter(snapshot)
    validate_snapshot(snapshot)
    current = today or date.today()
    limit = int(fields["stale_after_days"])
    return [
        provider
        for provider in PROVIDERS
        if (current - _provider_date(provider_section(snapshot, provider))).days > limit
    ]


def atomic_install(path: Path, snapshot: str) -> None:
    validate_snapshot(snapshot)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, delete=False
        ) as handle:
            handle.write(snapshot)
            temporary = Path(handle.name)
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage model routing calibration")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("--input", required=True)
    install = commands.add_parser("install")
    install.add_argument("--input", required=True)
    install.add_argument("--path")
    replace = commands.add_parser("replace-provider")
    replace.add_argument("--provider", choices=PROVIDERS, required=True)
    replace.add_argument("--input", required=True)
    replace.add_argument("--path")
    status = commands.add_parser("status")
    status.add_argument("--path")
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "validate":
            validate_snapshot(Path(args.input).read_text())
            print("valid")
            return 0
        path = target_path(args.path)
        if args.command == "install":
            atomic_install(path, Path(args.input).read_text())
            print(path)
            return 0
        if args.command == "replace-provider":
            current = path.read_text()
            updated = replace_provider(current, args.provider, Path(args.input).read_text())
            atomic_install(path, updated)
            print(path)
            return 0
        if not path.exists():
            print(json.dumps({"status": "missing", "path": str(path)}))
            return 0
        text = path.read_text()
        stale = stale_providers(text)
        print(json.dumps({
            "status": "stale" if stale else "fresh",
            "path": str(path),
            "stale_providers": stale,
        }))
        return 0
    except (OSError, SnapshotError) as error:
        if getattr(args, "command", None) == "status":
            print(json.dumps({"status": "invalid", "error": str(error)}))
            return 0
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run the snapshot tests**

Run:

```bash
python3 -m unittest tests/test_calibration_snapshot.py -v
```

Expected: 5 tests pass.

- [ ] **Step 6: Commit the helper**

```bash
git add calibrate-model-routing tests/test_calibration_snapshot.py
git commit -m "Add atomic model routing snapshot helper"
```

### Task 2: Write and Validate the Calibration Skill

**Files:**
- Modify: `calibrate-model-routing/SKILL.md`
- Modify: `calibrate-model-routing/agents/openai.yaml`

**Interfaces:**
- Consumes: `calibration_snapshot.py` CLI from Task 1.
- Produces: explicit `$calibrate-model-routing` workflow for both clients.
- Produces: a complete two-provider candidate or one validated provider section.

- [ ] **Step 1: Replace the scaffolded skill instructions**

Write `calibrate-model-routing/SKILL.md`:

```markdown
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
```

- [ ] **Step 2: Pin manual-only UI behavior**

Ensure `calibrate-model-routing/agents/openai.yaml` is exactly:

```yaml
interface:
  display_name: "Calibrate Model Routing"
  short_description: "Refresh Codex and Claude model routing guidance"
  default_prompt: "Use $calibrate-model-routing to refresh shared model and effort guidance from official sources."

policy:
  allow_implicit_invocation: false
```

- [ ] **Step 3: Run the official skill validator without installing a global Python package**

Run:

```bash
VALIDATOR_DEPS="$(mktemp -d)"
python3 -m pip install --quiet --target "$VALIDATOR_DEPS" PyYAML
PYTHONPATH="$VALIDATOR_DEPS" python3 \
  /Users/shai/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  calibrate-model-routing
rm -rf "$VALIDATOR_DEPS"
```

Expected: `Skill is valid!`

- [ ] **Step 4: Re-run focused tests and commit**

```bash
python3 -m unittest tests/test_calibration_snapshot.py -v
git add calibrate-model-routing
git commit -m "Add on-demand model routing calibration skill"
```

Expected: 5 tests pass, then the skill files commit cleanly.

### Task 3: Integrate Task-Specific Routing into Dispatch Compiler

**Files:**
- Create: `tests/test_markdown_contract.py`
- Modify: `SKILL.md`
- Modify: `templates/dispatch-calibration.md`
- Modify: `templates/successor-issue.md`
- Modify: `templates/project-profile.md`

**Interfaces:**
- Consumes: snapshot status and provider sections from Task 1.
- Consumes: existing packet `Complexity`, `Risk`, `Cost posture`, helper policy, and escalation conditions.
- Produces: `## Model routing` with independent `Codex` and `Claude` lines.

- [ ] **Step 1: Write failing Markdown contract tests**

Create `tests/test_markdown_contract.py`:

```python
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class MarkdownContractTests(unittest.TestCase):
    def test_successor_template_has_compact_separate_routing(self) -> None:
        text = (ROOT / "templates" / "successor-issue.md").read_text()
        self.assertIn("## Model routing", text)
        self.assertIn("- Codex:", text)
        self.assertIn("- Claude:", text)
        self.assertNotIn("Recommended Claude lane + effort", text)
        self.assertNotIn("Recommended Codex lane + effort", text)

    def test_core_skill_handles_fresh_stale_and_missing_snapshots(self) -> None:
        text = (ROOT / "SKILL.md").read_text()
        self.assertIn("calibration_snapshot.py status", text)
        self.assertIn("one non-blocking reminder", text)
        self.assertIn("Do not guess current model names", text)

    def test_project_profile_can_narrow_but_not_compare_providers(self) -> None:
        text = (ROOT / "templates" / "project-profile.md").read_text()
        self.assertIn("Allowed Codex models", text)
        self.assertIn("Allowed Claude models", text)
        self.assertIn("Low-cost shipping ownership", text)
        self.assertIn("Do not rank providers", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the contract tests to verify they fail**

Run:

```bash
python3 -m unittest tests/test_markdown_contract.py -v
```

Expected: 3 tests fail against the old generic recommendation fields.

- [ ] **Step 3: Add snapshot loading and routing rules to the core skill**

In `SKILL.md`, add this step after project-profile loading:

```markdown
3. Resolve `calibrate-model-routing/scripts/calibration_snapshot.py` relative
   to this skill and run `python3 calibration_snapshot.py status`. Read the
   shared snapshot before assigning current model names.
   - `fresh`: route normally.
   - `stale`: route from the last known-good snapshot and give the user one
     non-blocking reminder to run `$calibrate-model-routing`.
   - `missing` or `invalid`: compile the rest of the packet, mark model routing
     uncalibrated, and tell the user to run the calibrator. Do not guess current
     model names.
```

Replace the two recommended-lane fields in the skill's calibration example
with a separate block:

```markdown
## Model routing

- Codex: <starting model> / <effort> → <escalation model> / <effort> if the packet's escalation condition triggers.
- Claude: <starting model> / <effort> → <escalation model> / <effort> if the packet's escalation condition triggers.
```

Add this routing section immediately after `## Dispatch Calibration`:

```markdown
## Model Routing

Route Codex and Claude independently from the shared snapshot. Never recommend
one provider over the other.

For each provider:

1. Apply current catalog and effort semantics from the snapshot.
2. Narrow them with project availability and ownership constraints.
3. Choose the least expensive tier that can safely own this packet.
4. Raise model capability for genuine difficulty, unfamiliarity, ambiguity,
   or knowledge limits.
5. Raise effort for inspection depth, tool use, test execution, persistence,
   or verification burden.
6. Select a long-horizon specialist directly when the task is already larger
   than an ordinary sitting.
7. Add an arrow only when a materially stronger available route exists. Point
   it at the packet's existing escalation condition without copying it.

For `owner` or `needs-grill` work with no model-owned execution, emit `Not
applicable until ratified`. Low-cost helpers may own bounded evidence work, but
do not let them own shipping lanes by default.
```

- [ ] **Step 4: Update both packet templates**

Remove the two `Recommended ... lane + effort` lines from
`templates/dispatch-calibration.md` and `templates/successor-issue.md`.

Add this block immediately after dispatch calibration in both files:

```markdown
## Model routing

- Codex:
- Claude:
```

In `templates/dispatch-calibration.md`, replace the removed field guidance with:

```markdown
`Model routing` is generated per packet from the shared calibration snapshot,
project constraints, and this packet's traits. Name the starting model and
effort for each provider. Add an escalation target only when a materially
stronger route exists, and point to the packet's existing escalation condition
instead of repeating it. Do not rank providers.
```

- [ ] **Step 5: Add stable project-level constraints**

Replace `## Model Policy` in `templates/project-profile.md` with:

```markdown
## Model Policy

- Allowed Codex models:
- Unavailable Codex tiers:
- Allowed Claude models:
- Unavailable Claude tiers:
- Shipping lane default:
- When frontier or senior review is mandatory:
- Helper agent allowed tasks:
- Helper agent forbidden tasks:
- Low-cost shipping ownership: forbidden | mechanically-certain only | allowed
- Low-cost model stop conditions:
- Do not rank providers: true
```

- [ ] **Step 6: Run the contract and snapshot tests**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: 8 tests pass.

- [ ] **Step 7: Commit compiler integration**

```bash
git add SKILL.md templates tests/test_markdown_contract.py
git commit -m "Generate task-specific provider routing"
```

### Task 4: Migrate Examples and Documentation

**Files:**
- Modify: `examples/worked-example.md`
- Modify: `examples/worked-example-ci-log.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: compact routing contract from Task 3.
- Produces: installation and usage instructions for both skills and clients.

- [ ] **Step 1: Migrate every example calibration block**

Remove all `Recommended Claude lane + effort` and
`Recommended Codex lane + effort` fields from both example files. Add one of
these exact separate blocks after each dispatch calibration:

Routine implementation:

```markdown
## Model routing

- Codex: Terra / Medium → Sol / High if the packet's escalation condition triggers.
- Claude: Sonnet 5 / High → Opus 4.8 / XHigh if the packet's escalation condition triggers.
```

Bounded evidence/helper work:

```markdown
## Model routing

- Codex: Luna / Low → Terra / Medium if the packet's escalation condition triggers.
- Claude: Haiku 4.5 / Default → Sonnet 5 / High if the packet's escalation condition triggers.
```

Frontier-owned work:

```markdown
## Model routing

- Codex: Sol / High.
- Claude: Opus 4.8 / XHigh.
```

Owner or unratified work:

```markdown
## Model routing

- Codex: Not applicable until ratified.
- Claude: Not applicable until ratified.
```

Add one sentence before the first example routing block in each file:

```markdown
The model names below illustrate the calibration current when this example was
written; generated packets use the shared snapshot instead of copying them.
```

- [ ] **Step 2: Document installation and the calibration/routing split**

Add this installation block to `README.md` after the existing skill install:

```bash
# Optional but recommended: on-demand routing calibration
ln -s "$PWD/dispatch-compiler/calibrate-model-routing" \
  "${CODEX_HOME:-$HOME/.codex}/skills/calibrate-model-routing"
ln -s "$PWD/dispatch-compiler/calibrate-model-routing" \
  "$HOME/.claude/skills/calibrate-model-routing"
```

Add this section after `## Project profiles`:

```markdown
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
```

Under `What this does not do`, replace the old automatic-routing bullet with:

```markdown
- It does not choose a provider for the user or refresh model guidance without
  an explicit calibration run.
```

- [ ] **Step 3: Extend the Markdown contract test for examples and README**

Append these methods to `MarkdownContractTests` in
`tests/test_markdown_contract.py`:

```python
    def test_examples_use_compact_routing(self) -> None:
        for name in ("worked-example.md", "worked-example-ci-log.md"):
            text = (ROOT / "examples" / name).read_text()
            self.assertIn("## Model routing", text)
            self.assertNotIn("Recommended Claude lane + effort", text)
            self.assertNotIn("Recommended Codex lane + effort", text)

    def test_readme_explains_manual_shared_calibration(self) -> None:
        text = (ROOT / "README.md").read_text()
        self.assertIn("$calibrate-model-routing", text)
        self.assertIn("~/.agents/model-routing/calibration.md", text)
        self.assertIn("Calibration is never scheduled", text)
```

- [ ] **Step 4: Run full repository verification**

Run:

```bash
python3 -m unittest discover -s tests -v
if rg -n "Recommended (Claude|Codex) lane" \
  SKILL.md README.md templates examples
then
  exit 1
fi
git diff --check
```

Expected: 10 tests pass; `rg` finds no legacy recommendation fields; `git diff
--check` is silent.

- [ ] **Step 5: Re-run skill validation and commit docs**

```bash
VALIDATOR_DEPS="$(mktemp -d)"
python3 -m pip install --quiet --target "$VALIDATOR_DEPS" PyYAML
PYTHONPATH="$VALIDATOR_DEPS" python3 \
  /Users/shai/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  calibrate-model-routing
rm -rf "$VALIDATOR_DEPS"
git add README.md examples tests/test_markdown_contract.py
git commit -m "Document calibrated model routing"
```

Expected: `Skill is valid!`, followed by a clean commit.

### Task 5: Install Both Skills and Create the Initial Snapshot

**Files:**
- Create user-local links under `~/.codex/skills/` and `~/.claude/skills/`.
- Create user-local snapshot: `~/.agents/model-routing/calibration.md`.

**Interfaces:**
- Consumes: repository skills and helper from Tasks 1–4.
- Produces: discoverable skills in both clients and a fresh shared snapshot.

- [ ] **Step 1: Check for installation collisions without overwriting them**

Run:

```bash
for path in \
  "$HOME/.codex/skills/dispatch-compiler" \
  "$HOME/.codex/skills/calibrate-model-routing" \
  "$HOME/.claude/skills/dispatch-compiler" \
  "$HOME/.claude/skills/calibrate-model-routing"
do
  if [ -e "$path" ] || [ -L "$path" ]; then
    ls -ld "$path"
  fi
done
```

Expected: absent paths print nothing; existing paths are inspected. Stop and
resolve any path that points somewhere other than this repository.

- [ ] **Step 2: Install missing links**

Run only for paths confirmed absent:

```bash
mkdir -p "$HOME/.codex/skills" "$HOME/.claude/skills"
ln -s /Users/shai/Dev/dispatch-compiler \
  "$HOME/.codex/skills/dispatch-compiler"
ln -s /Users/shai/Dev/dispatch-compiler/calibrate-model-routing \
  "$HOME/.codex/skills/calibrate-model-routing"
ln -s /Users/shai/Dev/dispatch-compiler \
  "$HOME/.claude/skills/dispatch-compiler"
ln -s /Users/shai/Dev/dispatch-compiler/calibrate-model-routing \
  "$HOME/.claude/skills/calibrate-model-routing"
```

Expected: all four paths resolve into `/Users/shai/Dev/dispatch-compiler`.

- [ ] **Step 3: Run the newly installed calibration workflow**

In a fresh Codex or Claude task, invoke:

```text
Use $calibrate-model-routing to refresh both Codex and Claude guidance from
current official sources and create the shared snapshot.
```

Expected: official sources are cited, both provider sections validate, and the
snapshot is written to `~/.agents/model-routing/calibration.md` without a
scheduled task.

- [ ] **Step 4: Verify installation and freshness**

Run:

```bash
readlink "$HOME/.codex/skills/dispatch-compiler"
readlink "$HOME/.codex/skills/calibrate-model-routing"
readlink "$HOME/.claude/skills/dispatch-compiler"
readlink "$HOME/.claude/skills/calibrate-model-routing"
python3 \
  /Users/shai/Dev/dispatch-compiler/calibrate-model-routing/scripts/calibration_snapshot.py \
  status
```

Expected: each link targets this repository and status returns JSON with
`"status": "fresh"` and an empty `stale_providers` list.

- [ ] **Step 5: Run a no-write routing smoke matrix**

In a fresh task where both skills are discoverable, invoke:

```text
Use $dispatch-compiler in dry-run mode. Do not create or edit tracker items.
Using the current shared calibration, emit only the model-routing block for
each synthetic packet:

1. Ready, medium complexity, medium risk, ordinary implementation, explicit
   tests, and a bounded escalation condition.
2. Ready, XL complexity, high ambiguity, high autonomy, and already beyond an
   ordinary sitting.
3. Owner-only product decision with no implementation authorized.
```

Expected:

- Case 1 contains independent workhorse-to-frontier Codex and Claude lines.
- Case 2 starts each provider at the current appropriate frontier or
  long-horizon tier; Claude selects the snapshot's Fable tier directly when it
  is available and officially classified for that work.
- Case 3 says `Not applicable until ratified` for both providers.
- None of the cases recommends one provider over the other or repeats the full
  escalation condition.

- [ ] **Step 6: Verify final repository state**

Run:

```bash
python3 -m unittest discover -s tests -v
git diff --check
git status --short
```

Expected: 10 tests pass, diff check is silent, and the repository is clean.
