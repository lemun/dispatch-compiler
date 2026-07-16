from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install-grill-frontends.sh"


class GrillFrontendInstallTests(unittest.TestCase):
    def fixture(self, root: Path) -> tuple[dict[str, str], list[Path]]:
        home = root / "home"
        codex_home = root / "codex-home"
        home.mkdir()
        environment = os.environ.copy()
        environment.update({"HOME": str(home), "CODEX_HOME": str(codex_home)})
        destinations = [
            home / ".agents" / "skills" / "grill-me",
            home / ".agents" / "skills" / "grill-walk",
            home / ".claude" / "skills" / "grill-me",
            home / ".claude" / "skills" / "grill-walk",
        ]
        return environment, destinations

    def run_installer(self, environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
        self.assertTrue(INSTALLER.is_file(), "grill frontend installer is missing")
        return subprocess.run(
            ["bash", str(INSTALLER)],
            cwd="/",
            env=environment,
            capture_output=True,
            text=True,
        )

    def test_installs_four_direct_links_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            environment, destinations = self.fixture(Path(directory))

            first = self.run_installer(environment)
            self.assertEqual(first.returncode, 0, first.stderr)
            expected = [
                ROOT / "grill-me",
                ROOT / "grill-walk",
                ROOT / "grill-me-claude",
                ROOT / "grill-walk",
            ]
            for destination, source in zip(destinations, expected):
                self.assertTrue(destination.is_symlink())
                self.assertEqual(os.readlink(destination), str(source))

            second = self.run_installer(environment)
            self.assertEqual(second.returncode, 0, second.stderr)

    def test_any_destination_collision_stops_before_partial_install(self) -> None:
        for collision_index in range(4):
            with self.subTest(collision_index=collision_index):
                with tempfile.TemporaryDirectory() as directory:
                    environment, destinations = self.fixture(Path(directory))
                    collision = destinations[collision_index]
                    collision.mkdir(parents=True)
                    (collision / "sentinel.txt").write_text("preserve me\n")

                    result = self.run_installer(environment)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("Refusing to replace", result.stderr)
                    self.assertEqual(
                        (collision / "sentinel.txt").read_text(), "preserve me\n"
                    )
                    for index, destination in enumerate(destinations):
                        if index != collision_index:
                            self.assertFalse(
                                destination.exists() or destination.is_symlink(),
                                f"partially installed {destination}",
                            )

    def test_legacy_codex_copy_must_be_removed_before_install(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            environment, destinations = self.fixture(root)
            legacy = root / "codex-home" / "skills" / "grill-walk"
            legacy.mkdir(parents=True)
            (legacy / "SKILL.md").write_text("old duplicate\n")

            result = self.run_installer(environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate Codex-specific skill", result.stderr)
            self.assertTrue(legacy.is_dir())
            for destination in destinations:
                self.assertFalse(destination.exists() or destination.is_symlink())


if __name__ == "__main__":
    unittest.main()
