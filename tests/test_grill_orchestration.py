from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GRILL_WALK = ROOT / "grill-walk" / "SKILL.md"
GRILL_ME = ROOT / "grill-me" / "SKILL.md"
NEXTJS_PROFILE = ROOT / "profiles" / "homies-nextjs.md"
REACT_NATIVE_PROFILE = ROOT / "profiles" / "homies-react-native.md"
CLAUDE_GRILL_ME = ROOT / "grill-me-claude"

EXPECTED_GRILL_ME_METADATA = """interface:
  display_name: "Grill Me"
  short_description: "Sharpen one decision at a time"
  default_prompt: "Use $grill-me to interrogate this plan one consequential decision at a time."

policy:
  allow_implicit_invocation: false
"""

EXPECTED_GRILL_WALK_METADATA = """interface:
  display_name: "Grill Walk"
  short_description: "Turn a live walk into dispatchable evidence"
  default_prompt: "Use $grill-walk to walk this artifact, ratify findings, and compile the result into dispatchable work."

policy:
  allow_implicit_invocation: true
"""


class GrillOrchestrationContractTests(unittest.TestCase):
    def test_grill_me_keeps_claude_only_frontmatter_out_of_canonical_skill(self) -> None:
        canonical = GRILL_ME.read_text()
        self.assertNotIn("disable-model-invocation", canonical)

        entrypoint = CLAUDE_GRILL_ME / "SKILL.md"
        self.assertTrue(entrypoint.is_file(), "Claude grill-me entrypoint is missing")
        self.assertTrue(
            entrypoint.read_text().startswith(
                "---\n"
                "name: grill-me\n"
                "description: A relentless interview to sharpen a plan or design, with an optional explicit handoff to dispatch-compiler after decisions are ratified.\n"
                "disable-model-invocation: true\n"
                "---\n"
            )
        )
        workflow = CLAUDE_GRILL_ME / "WORKFLOW.md"
        self.assertTrue(workflow.is_symlink(), "Claude grill-me workflow is not a symlink")
        self.assertEqual(workflow.resolve(), GRILL_ME.resolve())

    def test_codex_discovery_metadata_matches_each_frontend(self) -> None:
        expected = {
            ROOT / "grill-me" / "agents" / "openai.yaml": EXPECTED_GRILL_ME_METADATA,
            ROOT
            / "grill-walk"
            / "agents"
            / "openai.yaml": EXPECTED_GRILL_WALK_METADATA,
        }
        for path, contents in expected.items():
            with self.subTest(path=path):
                self.assertTrue(path.is_file(), f"metadata is missing: {path}")
                self.assertEqual(path.read_text(), contents)

    def test_grill_walk_hands_off_compilation_instead_of_reimplementing_it(self) -> None:
        self.assertTrue(GRILL_WALK.is_file(), "versioned grill-walk skill is missing")
        text = GRILL_WALK.read_text()
        normalized = " ".join(text.split())

        self.assertIn("## Phase 3 - Compilation Handoff", text)
        self.assertIn("REQUIRED SUB-SKILL", text)
        self.assertIn("`dispatch-compiler`", text)
        for field in (
            "Source repository and source issue",
            "Session mode and evidence origin",
            "Ratified findings",
            "Vetoes and deliberate non-items",
            "Evidence and artifact paths",
            "Territory anchors",
            "Ranking and sequencing observations",
            "Unresolved owner calls",
            "Runtime proof status and blockers",
            "Project profile",
        ):
            with self.subTest(field=field):
                self.assertIn(field, normalized)

        for duplicated_policy in (
            "gh issue create",
            "Claude lane:",
            "Codex lane:",
            "Model/effort policy",
            "## Repo Tailoring",
        ):
            with self.subTest(duplicated_policy=duplicated_policy):
                self.assertNotIn(duplicated_policy, text)

    def test_grill_me_only_dispatches_when_the_user_requests_it(self) -> None:
        self.assertTrue(GRILL_ME.is_file(), "versioned grill-me skill is missing")
        text = GRILL_ME.read_text()
        normalized = " ".join(text.split())
        self.assertNotIn("/grilling", normalized)
        self.assertIn("Ask one question at a time", normalized)
        self.assertIn("provide a recommended answer", normalized)
        self.assertIn("If a fact can be found", normalized)
        self.assertIn("Do not enact the plan", normalized)
        self.assertIn("compile, dispatch, or file", normalized)
        self.assertIn("`dispatch-compiler`", normalized)
        self.assertIn("Otherwise, stop", normalized)

    def test_dispatch_compiler_accepts_a_ratified_grill_handoff(self) -> None:
        text = (ROOT / "SKILL.md").read_text()
        self.assertIn("compilation handoff", text.lower())
        self.assertIn("Do not re-grill ratified decisions", text)
        self.assertIn("profiles/homies-nextjs.md", text)
        self.assertIn("profiles/homies-react-native.md", text)

    def test_homies_nextjs_profile_encodes_board_runtime_and_pr_policy(self) -> None:
        self.assertTrue(NEXTJS_PROFILE.is_file(), "Homies Next.js profile is missing")
        text = NEXTJS_PROFILE.read_text()
        normalized = " ".join(text.split())
        for required in (
            "`ready`, `needs-grill`, `blocked`, `superseded`, and `owner`",
            "Only owner-ratified sessions may apply `ready`",
            "Leave unlabeled capture-inbox issues alone",
            "npm install",
            "npm run dev",
            "npm run build",
            "npm run test:e2e",
            "EN and HE",
            "desktop and mobile",
            "light and dark",
            "Mock production side effects",
            "What changed / Why it matters / What to check",
            "Closes #N",
            "Refs #N",
            "Conductor session can be archived",
        ):
            with self.subTest(required=required):
                self.assertIn(required, normalized)

    def test_homies_react_native_profile_encodes_lane_and_native_safety(self) -> None:
        self.assertTrue(
            REACT_NATIVE_PROFILE.is_file(), "Homies React Native profile is missing"
        )
        text = REACT_NATIVE_PROFILE.read_text()
        normalized = " ".join(text.split())
        for required in (
            "npm ci",
            "npm run dev",
            "npm run ci",
            "npm run e2e:smoke",
            "lane-local Metro port",
            "simulator or device",
            "dev client",
            "EN and HE",
            "RTL and dark mode",
            "runtimeVersion",
            "Never touch production Supabase casually",
            "one worktree and one branch",
            "Stage explicit paths only",
            "Closes #N",
            "Refs #N",
            "Conductor session can be archived",
        ):
            with self.subTest(required=required):
                self.assertIn(required, normalized)

    def test_homies_profiles_defer_current_model_names_to_calibration(self) -> None:
        hard_coded_models = ("terra", "sol", "luna", "opus", "sonnet", "haiku")
        for profile in (NEXTJS_PROFILE, REACT_NATIVE_PROFILE):
            self.assertTrue(profile.is_file(), f"profile is missing: {profile.name}")
            text = " ".join(profile.read_text().lower().split())
            with self.subTest(profile=profile.name):
                self.assertIn("do not rank providers: true", text)
                self.assertIn("shared calibration snapshot", text)
                for model in hard_coded_models:
                    self.assertNotRegex(text, rf"\b{model}\b")


if __name__ == "__main__":
    unittest.main()
