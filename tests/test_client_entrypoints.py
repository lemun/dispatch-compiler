from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DISPATCH_METADATA = ROOT / "agents" / "openai.yaml"
CODEX_METADATA = ROOT / "calibrate-model-routing" / "agents" / "openai.yaml"
CLAUDE_ENTRYPOINT = ROOT / "calibrate-model-routing-claude"
CLAUDE_SKILL = CLAUDE_ENTRYPOINT / "SKILL.md"
CANONICAL_SKILL = ROOT / "calibrate-model-routing" / "SKILL.md"
CANONICAL_SCRIPTS = ROOT / "calibrate-model-routing" / "scripts"

EXPECTED_CODEX_METADATA = """interface:
  display_name: "Calibrate Model Routing"
  short_description: "Refresh Codex and Claude model routing guidance"
  default_prompt: "Use $calibrate-model-routing to refresh shared model and effort guidance from official sources."

policy:
  allow_implicit_invocation: false
"""

EXPECTED_DISPATCH_METADATA = """interface:
  display_name: "Dispatch Compiler"
  short_description: "Compile evidence into dispatchable agent work"
  default_prompt: "Use $dispatch-compiler to turn this charter or evidence into proof-gated, merge-safe successor work."

policy:
  allow_implicit_invocation: true
"""

EXPECTED_CLAUDE_FRONTMATTER = """---
name: calibrate-model-routing
description: Refresh the shared Codex and Claude model-routing calibration from current official provider documentation. Use only when the user explicitly invokes this skill after provider model, effort, alias, availability, or guidance changes.
disable-model-invocation: true
---
"""


class ClientEntrypointTests(unittest.TestCase):
    def test_dispatch_compiler_explicitly_allows_implicit_invocation(self) -> None:
        self.assertEqual(DISPATCH_METADATA.read_text(), EXPECTED_DISPATCH_METADATA)

    def test_codex_entrypoint_uses_exact_manual_only_metadata(self) -> None:
        self.assertEqual(CODEX_METADATA.read_text(), EXPECTED_CODEX_METADATA)

    def test_claude_entrypoint_starts_with_exact_manual_only_frontmatter(self) -> None:
        self.assertTrue(CLAUDE_SKILL.is_file(), "Claude SKILL.md is missing")
        self.assertTrue(CLAUDE_SKILL.read_text().startswith(EXPECTED_CLAUDE_FRONTMATTER))

    def test_claude_entrypoint_delegates_to_canonical_paths(self) -> None:
        self.assertTrue(CLAUDE_SKILL.is_file(), "Claude SKILL.md is missing")
        body = CLAUDE_SKILL.read_text().split("---", 2)[2]
        self.assertIn("${CLAUDE_SKILL_DIR}/WORKFLOW.md", body)
        self.assertIn(
            "${CLAUDE_SKILL_DIR}/scripts/calibration_snapshot.py",
            body,
        )

    def test_claude_workflow_resolves_to_canonical_skill(self) -> None:
        workflow = CLAUDE_ENTRYPOINT / "WORKFLOW.md"
        self.assertTrue(workflow.is_symlink(), "Claude WORKFLOW.md is not a symlink")
        self.assertEqual(workflow.resolve(), CANONICAL_SKILL.resolve())

    def test_claude_scripts_resolve_to_canonical_scripts(self) -> None:
        scripts = CLAUDE_ENTRYPOINT / "scripts"
        self.assertTrue(scripts.is_symlink(), "Claude scripts is not a symlink")
        self.assertEqual(scripts.resolve(), CANONICAL_SCRIPTS.resolve())


if __name__ == "__main__":
    unittest.main()
