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
