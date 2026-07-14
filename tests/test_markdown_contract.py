from pathlib import Path
import re
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
        self.assertIn("Resolve `CALIBRATION_HELPER` to the absolute path", text)
        self.assertIn('python3 "$CALIBRATION_HELPER" status', text)
        self.assertIn("one non-blocking reminder", text)
        self.assertIn("stale-snapshot reminder in chat only", text)
        self.assertIn("must not appear in a generated issue or packet", text)
        self.assertIn("Do not guess current model names", text)

    def test_project_profile_can_narrow_but_not_compare_providers(self) -> None:
        text = (ROOT / "templates" / "project-profile.md").read_text()
        self.assertIn("Allowed Codex models", text)
        self.assertIn("Allowed Claude models", text)
        self.assertIn("Low-cost shipping ownership", text)
        self.assertIn("Do not rank providers", text)

    def test_examples_use_compact_routing(self) -> None:
        for name in ("worked-example.md", "worked-example-ci-log.md"):
            text = (ROOT / "examples" / name).read_text()
            self.assertIn("## Model routing", text)
            self.assertNotIn("Recommended Claude lane + effort", text)
            self.assertNotIn("Recommended Codex lane + effort", text)

    def test_ci_example_routes_every_successor_including_owner_work(self) -> None:
        text = (ROOT / "examples" / "worked-example-ci-log.md").read_text()
        successors = re.split(r"(?m)^## Successor issue \d of 4$", text)[1:]
        self.assertEqual(len(successors), 4)
        for number, successor in enumerate(successors, start=1):
            with self.subTest(successor=number):
                self.assertEqual(successor.count("## Dispatch calibration"), 1)
                self.assertEqual(successor.count("## Model routing"), 1)
                self.assertEqual(successor.count("- Codex:"), 1)
                self.assertEqual(successor.count("- Claude:"), 1)
        owner = successors[3]
        self.assertIn("- Codex: Not applicable until ratified.", owner)
        self.assertIn("- Claude: Not applicable until ratified.", owner)

    def test_readme_explains_manual_shared_calibration(self) -> None:
        text = (ROOT / "README.md").read_text()
        self.assertIn("$calibrate-model-routing", text)
        self.assertIn("~/.agents/model-routing/calibration.md", text)
        self.assertIn("Calibration is never scheduled", text)

    def test_calibrator_preflights_and_preserves_mixed_refresh_outcomes(self) -> None:
        text = (ROOT / "calibrate-model-routing" / "SKILL.md").read_text()
        normalized = " ".join(text.split())
        self.assertIn("## Preflight", text)
        self.assertLess(text.index("## Preflight"), text.index("## Research"))
        self.assertIn("Read the existing snapshot before research", normalized)
        self.assertIn("apply only successfully completed provider sections", normalized)
        self.assertIn("preserve each incomplete provider section byte-for-byte", normalized)
        self.assertIn("run `replace-provider` once per completed provider", normalized)
        self.assertIn("Never install a partial first snapshot", normalized)
        self.assertIn("both complete provider sections validate", normalized)

    def test_calibrator_commands_use_an_absolute_helper_from_any_cwd(self) -> None:
        text = (ROOT / "calibrate-model-routing" / "SKILL.md").read_text()
        self.assertIn("Set `CALIBRATION_HELPER` to the absolute path", text)
        self.assertGreaterEqual(text.count('python3 "$CALIBRATION_HELPER"'), 3)
        self.assertNotIn("python3 scripts/calibration_snapshot.py", text)


if __name__ == "__main__":
    unittest.main()
