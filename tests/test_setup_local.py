"""
Unit tests for setup_local.py — lightwarp/config/local.py generator.

Run from the pipeline/ directory:
    python -m pytest tests/test_setup_local.py
"""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from setup_local import _is_lightwarp_root, _write_local_py

# Override _LOCAL_PY for tests so we never touch the real lightwarp/config/local.py.
import setup_local as _sl


class TestIsLightwarpRoot(unittest.TestCase):
    def test_returns_true_when_all_markers_present(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for d in ("projects", "pipeline", "lib"):
                (root / d).mkdir()
            self.assertTrue(_is_lightwarp_root(root))

    def test_returns_false_when_marker_missing(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "projects").mkdir()
            (root / "pipeline").mkdir()
            self.assertFalse(_is_lightwarp_root(root))

    def test_returns_false_for_empty_directory(self):
        with TemporaryDirectory() as tmp:
            self.assertFalse(_is_lightwarp_root(Path(tmp)))

    def test_returns_false_for_nonexistent_path(self):
        self.assertFalse(_is_lightwarp_root(Path("/nonexistent_xyz_123")))


class TestWriteLocalPy(unittest.TestCase):
    def test_writes_valid_python_with_drive_root(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "local.py"
            original = _sl._LOCAL_PY
            try:
                _sl._LOCAL_PY = target
                drive = Path("G:/Shared drives/LightWarp_Test")
                _write_local_py(drive)

                content = target.read_text(encoding="utf-8")
                self.assertIn("from pathlib import Path", content)
                self.assertIn("DRIVE_ROOT", content)
                self.assertIn("G:/Shared drives/LightWarp_Test", content)

                ns: dict = {}
                exec(content, ns)
                self.assertEqual(ns["DRIVE_ROOT"], drive)
            finally:
                _sl._LOCAL_PY = original

    def test_uses_posix_slashes(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "local.py"
            original = _sl._LOCAL_PY
            try:
                _sl._LOCAL_PY = target
                _write_local_py(Path("C:\\Users\\dev\\LightWarp"))

                content = target.read_text(encoding="utf-8")
                self.assertNotIn("\\\\", content)
                self.assertIn("C:/Users/dev/LightWarp", content)
            finally:
                _sl._LOCAL_PY = original


if __name__ == "__main__":
    unittest.main()
