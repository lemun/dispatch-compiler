from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
INSTALL_MARKER = "# Install all four skill links with collision checks"


class ReadmeInstallTests(unittest.TestCase):
    def installer_script(self) -> str:
        text = README.read_text()
        self.assertIn(INSTALL_MARKER, text)
        marker = text.index(INSTALL_MARKER)
        end = text.index("```", marker)
        return text[marker:end]

    def fixture(self, root: Path) -> tuple[Path, dict[str, str], list[Path]]:
        checkout = root / "checkout"
        repository = checkout / "dispatch-compiler"
        (repository / "calibrate-model-routing").mkdir(parents=True)
        (repository / "calibrate-model-routing-claude").mkdir()
        (repository / "sentinel.txt").write_text("source must stay unchanged\n")
        home = root / "home"
        codex_home = root / "codex-home"
        home.mkdir()
        environment = os.environ.copy()
        environment.update({"HOME": str(home), "CODEX_HOME": str(codex_home)})
        destinations = [
            codex_home / "skills" / "dispatch-compiler",
            codex_home / "skills" / "calibrate-model-routing",
            home / ".claude" / "skills" / "dispatch-compiler",
            home / ".claude" / "skills" / "calibrate-model-routing",
        ]
        return checkout, environment, destinations

    def run_installer(self, cwd: Path, environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", "-c", self.installer_script()],
            cwd=cwd,
            env=environment,
            capture_output=True,
            text=True,
        )

    def test_rerun_is_a_noop_for_all_four_exact_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            checkout, environment, destinations = self.fixture(Path(directory))
            first = self.run_installer(checkout, environment)
            self.assertEqual(first.returncode, 0, first.stderr)
            source = Path(os.path.realpath(checkout)) / "dispatch-compiler"
            expected_targets = [
                source,
                source / "calibrate-model-routing",
                source,
                source / "calibrate-model-routing-claude",
            ]
            for destination, expected in zip(destinations, expected_targets):
                self.assertTrue(destination.is_symlink())
                self.assertEqual(os.readlink(destination), str(expected))

            source_before = sorted(
                str(path.relative_to(source)) for path in source.rglob("*")
            )
            second = self.run_installer(checkout, environment)
            self.assertEqual(second.returncode, 0, second.stderr)
            source_after = sorted(
                str(path.relative_to(source)) for path in source.rglob("*")
            )
            self.assertEqual(source_after, source_before)

    def test_mismatched_symlink_at_any_position_stops_before_installing(self) -> None:
        for collision_index in reversed(range(4)):
            with self.subTest(collision_index=collision_index):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    checkout, environment, destinations = self.fixture(root)
                    mismatch = destinations[collision_index]
                    mismatch.parent.mkdir(parents=True, exist_ok=True)
                    wrong_target = root / "wrong-source"
                    wrong_target.mkdir()
                    sentinel = wrong_target / "sentinel.txt"
                    sentinel.write_text("leave this target alone\n")
                    mismatch.symlink_to(wrong_target)

                    result = self.run_installer(checkout, environment)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("Refusing to replace", result.stderr)
                    self.assertEqual(os.readlink(mismatch), str(wrong_target))
                    self.assertEqual(sentinel.read_text(), "leave this target alone\n")
                    for index, destination in enumerate(destinations):
                        if index != collision_index:
                            self.assertFalse(
                                destination.exists() or destination.is_symlink(),
                                f"partially installed {destination}",
                            )

    def test_non_symlink_collision_at_any_position_stops_before_installing(self) -> None:
        for collision_index in reversed(range(4)):
            with self.subTest(collision_index=collision_index):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    checkout, environment, destinations = self.fixture(root)
                    collision = destinations[collision_index]
                    collision.mkdir(parents=True)
                    sentinel = collision / "sentinel.txt"
                    sentinel.write_text("leave this collision alone\n")

                    result = self.run_installer(checkout, environment)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("Refusing to replace", result.stderr)
                    self.assertTrue(collision.is_dir())
                    self.assertFalse(collision.is_symlink())
                    self.assertEqual(
                        sentinel.read_text(),
                        "leave this collision alone\n",
                    )
                    for index, destination in enumerate(destinations):
                        if index != collision_index:
                            self.assertFalse(
                                destination.exists() or destination.is_symlink(),
                                f"partially installed {destination}",
                            )


if __name__ == "__main__":
    unittest.main()
