from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CODEX_METADATA = ROOT / "calibrate-model-routing" / "agents" / "openai.yaml"
CLAUDE_ENTRYPOINT = ROOT / "calibrate-model-routing-claude"
CLAUDE_SKILL = CLAUDE_ENTRYPOINT / "SKILL.md"
CANONICAL_SKILL = ROOT / "calibrate-model-routing" / "SKILL.md"
CANONICAL_SCRIPTS = ROOT / "calibrate-model-routing" / "scripts"


def frontmatter(path: Path) -> str:
    text = path.read_text()
    opening, metadata, _body = text.split("---", 2)
    if opening:
        raise AssertionError(f"{path} does not begin with YAML frontmatter")
    return metadata


class ClientEntrypointTests(unittest.TestCase):
    def test_codex_entrypoint_disables_implicit_invocation(self) -> None:
        self.assertIn(
            "allow_implicit_invocation: false",
            CODEX_METADATA.read_text(),
        )

    def test_claude_entrypoint_disables_model_invocation(self) -> None:
        self.assertTrue(CLAUDE_SKILL.is_file(), "Claude SKILL.md is missing")
        self.assertIn("disable-model-invocation: true", frontmatter(CLAUDE_SKILL))

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
