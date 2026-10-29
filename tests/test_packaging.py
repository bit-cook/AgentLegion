"""Version alignment: pyproject, package __version__, README badge text."""
import re
import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestVersionAlignment(unittest.TestCase):
    def test_pyproject_version_matches_package(self):
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertIn("dynamic", pyproject["project"])
        self.assertIn("version", pyproject["project"]["dynamic"])
        self.assertEqual(
            pyproject["tool"]["setuptools"]["dynamic"]["version"]["attr"],
            "agent_legion.version.__version__",
        )
        from agent_legion import __version__

        self.assertEqual(__version__, "1.0.0")

    def test_readme_badges_reference_existing_workflow(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(
            "https://github.com/bit-cook/AgentLegion/actions/workflows/ci.yml/badge.svg",
            readme,
        )
        self.assertTrue((REPO_ROOT / ".github" / "workflows" / "ci.yml").exists())

    def test_license_file_exists_and_matches_claim(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("MIT License", readme)
        license_text = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("MIT License", license_text)
        self.assertIn("Permission is hereby granted", license_text)

    def test_requirements_install_nothing(self):
        """requirements.txt must not declare phantom dependencies."""
        requirements = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8")
        package_lines = [
            line.strip()
            for line in requirements.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        self.assertEqual(package_lines, [])


if __name__ == "__main__":
    unittest.main()
