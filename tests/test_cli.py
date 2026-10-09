"""Exercise the installed package's command-line interface."""

import subprocess
import sys
import unittest

from aderrr import __version__


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "aderrr", *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_default_command(self) -> None:
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("aderrr is ready", result.stdout)

    def test_version(self) -> None:
        result = self.run_cli("--version")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), __version__)

    def test_invalid_option(self) -> None:
        result = self.run_cli("--unknown-option")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unrecognized arguments", result.stderr)
