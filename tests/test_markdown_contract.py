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


if __name__ == "__main__":
    unittest.main()
