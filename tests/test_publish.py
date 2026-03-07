"""
Unit tests for publish.py — the dev-to-production promotion script.

Tests the pure helper functions (no Drive side-effects).

Run from the pipeline/ directory:
    python -m unittest tests.test_publish
"""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from publish import _collect_files, _diff_area, _remove_empty_dirs, _should_skip


class TestShouldSkip(unittest.TestCase):
    """_should_skip must filter out build artifacts and OS junk."""

    def test_pycache(self):
        self.assertTrue(_should_skip(Path("__pycache__/foo.cpython-311.pyc")))

    def test_pyc_extension(self):
        self.assertTrue(_should_skip(Path("module.pyc")))

    def test_pyo_extension(self):
        self.assertTrue(_should_skip(Path("module.pyo")))

    def test_ds_store(self):
        self.assertTrue(_should_skip(Path(".DS_Store")))

    def test_thumbs_db(self):
        self.assertTrue(_should_skip(Path("Thumbs.db")))

    def test_desktop_ini(self):
        self.assertTrue(_should_skip(Path("desktop.ini")))

    def test_egg_info(self):
        self.assertTrue(_should_skip(Path("pkg.egg-info/PKG-INFO")))

    def test_venv(self):
        self.assertTrue(_should_skip(Path(".venv/lib/foo.py")))

    def test_git(self):
        self.assertTrue(_should_skip(Path(".git/config")))

    def test_normal_py(self):
        self.assertFalse(_should_skip(Path("core.py")))

    def test_normal_nested(self):
        self.assertFalse(_should_skip(Path("proj_folders/gui.py")))

    def test_init_py(self):
        self.assertFalse(_should_skip(Path("proj_folders/__init__.py")))


class TestCollectFiles(unittest.TestCase):
    def test_collects_files(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_text("a")
            (root / "sub").mkdir()
            (root / "sub" / "b.py").write_text("b")
            result = _collect_files(root)
            self.assertEqual(result, {"a.py", "sub/b.py"})

    def test_skips_pycache(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "__pycache__").mkdir()
            (root / "__pycache__" / "mod.cpython-311.pyc").write_bytes(b"")
            (root / "core.py").write_text("code")
            result = _collect_files(root)
            self.assertEqual(result, {"core.py"})

    def test_missing_directory(self):
        result = _collect_files(Path("/nonexistent/path/xyz"))
        self.assertEqual(result, set())


class TestDiffArea(unittest.TestCase):
    def test_all_new(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            dst = Path(tmp) / "dst"
            src.mkdir()
            dst.mkdir()
            (src / "a.py").write_text("hello")
            to_add, to_update, to_remove, unchanged = _diff_area(src, dst)
            self.assertEqual(to_add, ["a.py"])
            self.assertEqual(to_update, [])
            self.assertEqual(to_remove, [])
            self.assertEqual(unchanged, [])

    def test_unchanged(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            dst = Path(tmp) / "dst"
            src.mkdir()
            dst.mkdir()
            (src / "a.py").write_text("same")
            (dst / "a.py").write_text("same")
            to_add, to_update, to_remove, unchanged = _diff_area(src, dst)
            self.assertEqual(to_add, [])
            self.assertEqual(to_update, [])
            self.assertEqual(to_remove, [])
            self.assertEqual(unchanged, ["a.py"])

    def test_updated(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            dst = Path(tmp) / "dst"
            src.mkdir()
            dst.mkdir()
            (src / "a.py").write_text("new version")
            (dst / "a.py").write_text("old version")
            to_add, to_update, to_remove, unchanged = _diff_area(src, dst)
            self.assertEqual(to_add, [])
            self.assertEqual(to_update, ["a.py"])
            self.assertEqual(to_remove, [])
            self.assertEqual(unchanged, [])

    def test_stale_removed(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            dst = Path(tmp) / "dst"
            src.mkdir()
            dst.mkdir()
            (dst / "old.py").write_text("stale")
            to_add, to_update, to_remove, unchanged = _diff_area(src, dst)
            self.assertEqual(to_add, [])
            self.assertEqual(to_update, [])
            self.assertEqual(to_remove, ["old.py"])
            self.assertEqual(unchanged, [])

    def test_mixed(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            dst = Path(tmp) / "dst"
            src.mkdir()
            dst.mkdir()

            (src / "new.py").write_text("new")
            (src / "changed.py").write_text("v2")
            (src / "same.py").write_text("same")

            (dst / "changed.py").write_text("v1")
            (dst / "same.py").write_text("same")
            (dst / "stale.py").write_text("stale")

            to_add, to_update, to_remove, unchanged = _diff_area(src, dst)
            self.assertEqual(to_add, ["new.py"])
            self.assertEqual(to_update, ["changed.py"])
            self.assertEqual(to_remove, ["stale.py"])
            self.assertEqual(unchanged, ["same.py"])

    def test_nested_files(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            dst = Path(tmp) / "dst"
            src.mkdir()
            dst.mkdir()

            (src / "pkg").mkdir()
            (src / "pkg" / "__init__.py").write_text("")
            (src / "pkg" / "core.py").write_text("code")

            to_add, to_update, to_remove, unchanged = _diff_area(src, dst)
            self.assertEqual(sorted(to_add), ["pkg/__init__.py", "pkg/core.py"])

    def test_dst_not_exists(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            dst = Path(tmp) / "dst"
            src.mkdir()
            (src / "a.py").write_text("code")
            to_add, to_update, to_remove, unchanged = _diff_area(src, dst)
            self.assertEqual(to_add, ["a.py"])


class TestRemoveEmptyDirs(unittest.TestCase):
    def test_removes_empty_leaf(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            empty = root / "a" / "b"
            empty.mkdir(parents=True)
            _remove_empty_dirs(root)
            self.assertFalse((root / "a").exists())

    def test_preserves_dirs_with_files(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "keep").mkdir()
            (root / "keep" / "file.py").write_text("x")
            (root / "keep" / "empty").mkdir()
            _remove_empty_dirs(root)
            self.assertTrue((root / "keep").is_dir())
            self.assertFalse((root / "keep" / "empty").exists())

    def test_noop_missing_dir(self):
        _remove_empty_dirs(Path("/nonexistent/path/xyz"))


if __name__ == "__main__":
    unittest.main()
