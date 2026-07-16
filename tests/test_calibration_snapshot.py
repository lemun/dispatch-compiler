from __future__ import annotations

import importlib.util
import fcntl
import subprocess
import sys
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

SCALAR_FIELDS = (
    "Verified at",
    "Client or account constraints",
    "Workhorse",
    "Frontier",
    "Long-horizon or exceptional tier",
    "Helper or high-volume tier",
    "Effort guidance",
    "Routing notes",
)


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

    def test_accepts_multiple_official_provider_sources(self) -> None:
        candidate = CODEX.replace(
            "  - https://developers.openai.com/api/docs/guides/latest-model\n",
            "  - https://developers.openai.com/api/docs/guides/latest-model\n"
            "  - https://openai.com/research\n",
        )
        snapshot.validate_provider_section("codex", candidate)

    def test_rejects_invalid_items_after_valid_official_source(self) -> None:
        invalid_items = {
            "http_url": "  - http://developers.openai.com/insecure\n",
            "malformed_item": "  - not-a-url\n",
            "stray_text": "  unexpected nested text\n",
            "nonofficial_https": "  - https://example.com/not-official\n",
            "nested_item": "    - https://openai.com/research\n",
            "multiple_urls": (
                "  - https://openai.com/research https://openai.com/news\n"
            ),
        }
        official_source = (
            "  - https://developers.openai.com/api/docs/guides/latest-model\n"
        )
        for name, invalid_item in invalid_items.items():
            with self.subTest(name=name):
                candidate = CODEX.replace(
                    official_source,
                    official_source + invalid_item,
                )
                with self.assertRaises(snapshot.SnapshotError):
                    snapshot.validate_provider_section("codex", candidate)

    def test_rejects_blank_provider_scalar_fields(self) -> None:
        for field in SCALAR_FIELDS:
            with self.subTest(field=field):
                prefix = f"- {field}:"
                lines = [
                    f"{prefix}   " if line.startswith(prefix) else line
                    for line in CODEX.splitlines()
                ]
                with self.assertRaises(snapshot.SnapshotError):
                    snapshot.validate_provider_section("codex", "\n".join(lines) + "\n")

    def test_rejects_empty_official_sources(self) -> None:
        bad = CODEX.replace(
            "  - https://developers.openai.com/api/docs/guides/latest-model\n",
            "",
        )
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.validate_provider_section("codex", bad)

    def test_rejects_duplicate_required_provider_field(self) -> None:
        bad = CODEX.replace(
            "- Workhorse: Terra / Medium for ordinary implementation.\n",
            "- Workhorse: Terra / Medium for ordinary implementation.\n"
            "- Workhorse: Duplicate value must not be accepted.\n",
        )
        with self.assertRaisesRegex(snapshot.SnapshotError, "exactly once"):
            snapshot.validate_provider_section("codex", bad)

    def test_rejects_duplicate_provider_sections(self) -> None:
        duplicates = {
            "codex": CODEX.replace(
                "2026-07-14",
                "2099-01-01",
            ).replace(
                "https://developers.openai.com/api/docs/guides/latest-model",
                "https://example.com/unofficial",
            ),
            "claude": CLAUDE,
        }
        for provider, duplicate in duplicates.items():
            with self.subTest(provider=provider):
                candidate = full_snapshot() + "\n" + duplicate
                with self.assertRaisesRegex(snapshot.SnapshotError, "exactly one"):
                    snapshot.validate_snapshot(candidate, today=date(2026, 7, 14))

    def test_rejects_official_url_outside_official_sources_list(self) -> None:
        bad = CODEX.replace(
            "  - https://developers.openai.com/api/docs/guides/latest-model\n",
            "",
        ).replace(
            "- Workhorse: Terra / Medium for ordinary implementation.",
            "- Workhorse: https://developers.openai.com/api/docs/guides/latest-model",
        )
        with self.assertRaisesRegex(snapshot.SnapshotError, "Official sources"):
            snapshot.validate_provider_section("codex", bad)

    def test_rejects_verification_date_after_effective_date(self) -> None:
        candidate = CODEX.replace("2026-07-14", "2026-07-15")
        with self.assertRaisesRegex(snapshot.SnapshotError, "future"):
            snapshot.validate_provider_section(
                "codex",
                candidate,
                today=date(2026, 7, 14),
            )
        snapshot.validate_provider_section(
            "codex",
            candidate,
            today=date(2026, 7, 15),
        )

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

    def test_concurrent_cli_provider_replacements_preserve_both_updates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "nested" / "calibration.md"
            snapshot.atomic_install(target, full_snapshot())
            codex_candidate = root / "codex.md"
            codex_candidate.write_text(
                CODEX.replace("2026-07-14", "2026-07-15").replace(
                    "Terra / Medium", "Codex concurrent update / Medium"
                )
            )
            claude_candidate = root / "claude.md"
            claude_candidate.write_text(
                CLAUDE.replace("2026-07-14", "2026-07-15").replace(
                    "Sonnet 5 / High", "Claude concurrent update / High"
                )
            )

            lock_path = Path(f"{target}.lock")
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            with lock_path.open("a+") as held_lock:
                fcntl.flock(held_lock, fcntl.LOCK_EX)
                processes = [
                    subprocess.Popen(
                        [
                            sys.executable,
                            str(SCRIPT),
                            "replace-provider",
                            "--provider",
                            provider,
                            "--input",
                            str(candidate),
                            "--path",
                            str(target),
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    for provider, candidate in (
                        ("codex", codex_candidate),
                        ("claude", claude_candidate),
                    )
                ]
                blocked = []
                try:
                    for process in processes:
                        try:
                            process.wait(timeout=1)
                        except subprocess.TimeoutExpired:
                            blocked.append(True)
                        else:
                            blocked.append(False)
                finally:
                    fcntl.flock(held_lock, fcntl.LOCK_UN)

            results = [process.communicate(timeout=5) for process in processes]
            self.assertEqual(blocked, [True, True], "replacements bypassed the lock")
            for process, (_, stderr) in zip(processes, results):
                self.assertEqual(process.returncode, 0, stderr)
            installed = target.read_text()
            self.assertIn("Codex concurrent update / Medium", installed)
            self.assertIn("Claude concurrent update / High", installed)

    def test_cli_install_status_and_replace_work_from_unrelated_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            unrelated = root / "unrelated-cwd"
            unrelated.mkdir()
            target = root / "state" / "calibration.md"
            candidate = root / "candidate.md"
            candidate.write_text(full_snapshot())

            install = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "install",
                    "--input",
                    str(candidate),
                    "--path",
                    str(target),
                ],
                cwd=unrelated,
                capture_output=True,
                text=True,
            )
            self.assertEqual(install.returncode, 0, install.stderr)

            status = subprocess.run(
                [sys.executable, str(SCRIPT), "status", "--path", str(target)],
                cwd=unrelated,
                capture_output=True,
                text=True,
            )
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertIn('"status": "fresh"', status.stdout)

            replacement = root / "codex.md"
            replacement.write_text(
                CODEX.replace("Terra / Medium", "Arbitrary CWD / Medium")
            )
            replace = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "replace-provider",
                    "--provider",
                    "codex",
                    "--input",
                    str(replacement),
                    "--path",
                    str(target),
                ],
                cwd=unrelated,
                capture_output=True,
                text=True,
            )
            self.assertEqual(replace.returncode, 0, replace.stderr)
            self.assertIn("Arbitrary CWD / Medium", target.read_text())


if __name__ == "__main__":
    unittest.main()
