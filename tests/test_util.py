"""
Unit tests for lightwarp.util — cross-platform utility helpers.

Run from the pipeline/ directory:
    python -m pytest tests/test_util.py
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from lightwarp.util import log_to_project


class TestLogToProject(unittest.TestCase):
    def test_creates_log_file_and_writes_message(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_to_project(root, "test_tool", "hello world")
            log_file = root / "utils" / "logs" / "test_tool.log"
            self.assertTrue(log_file.is_file())
            content = log_file.read_text(encoding="utf-8")
            self.assertIn("hello world", content)

    def test_creates_log_directory_structure(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_to_project(root, "tool", "msg")
            self.assertTrue((root / "utils" / "logs").is_dir())

    def test_appends_multiple_messages(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_to_project(root, "tool", "first")
            log_to_project(root, "tool", "second")
            log_file = root / "utils" / "logs" / "tool.log"
            lines = log_file.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 2)
            self.assertIn("first", lines[0])
            self.assertIn("second", lines[1])

    def test_includes_timestamp(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_to_project(root, "tool", "msg")
            content = (root / "utils" / "logs" / "tool.log").read_text(encoding="utf-8")
            self.assertRegex(content, r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]")

    def test_never_raises_on_failure(self):
        # Passing a non-writable path should not raise — log_to_project swallows errors.
        try:
            log_to_project(Path("/nonexistent_xyz_123/bad"), "tool", "msg")
        except Exception:
            self.fail("log_to_project raised an exception on an invalid path")

    def test_separate_tools_get_separate_files(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_to_project(root, "alpha", "a-msg")
            log_to_project(root, "beta", "b-msg")
            a = (root / "utils" / "logs" / "alpha.log").read_text(encoding="utf-8")
            b = (root / "utils" / "logs" / "beta.log").read_text(encoding="utf-8")
            self.assertIn("a-msg", a)
            self.assertNotIn("b-msg", a)
            self.assertIn("b-msg", b)


if __name__ == "__main__":
    unittest.main()
