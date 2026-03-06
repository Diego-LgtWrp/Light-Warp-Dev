"""
Unit tests for deploy.py — the Drive sync script.

Tests the pure helper functions (no git or filesystem side-effects).

Run from the pipeline/ directory:
    python -m pytest tests/test_deploy.py
"""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from deploy import _remove_empty_dirs, _should_preserve, _walk_target


class TestShouldPreserve(unittest.TestCase):
    """_should_preserve must protect runtime artifacts from deletion."""

    def test_pycache_directory(self):
        self.assertTrue(_should_preserve("config/__pycache__/__init__.cpython-314.pyc"))

    def test_pycache_at_root(self):
        self.assertTrue(_should_preserve("__pycache__/foo.cpython-311.pyc"))

    def test_pyc_extension(self):
        self.assertTrue(_should_preserve("lightwarp/env.pyc"))

    def test_pyo_extension(self):
        self.assertTrue(_should_preserve("lightwarp/env.pyo"))

    def test_config_local_py(self):
        self.assertTrue(_should_preserve("config/local.py"))

    def test_venv_directory(self):
        self.assertTrue(_should_preserve(".venv/lib/site-packages/foo.py"))

    def test_vscode_directory(self):
        self.assertTrue(_should_preserve(".vscode/settings.json"))

    def test_idea_directory(self):
        self.assertTrue(_should_preserve(".idea/workspace.xml"))

    def test_ds_store(self):
        self.assertTrue(_should_preserve(".DS_Store"))

    def test_thumbs_db(self):
        self.assertTrue(_should_preserve("Thumbs.db"))

    def test_desktop_ini(self):
        self.assertTrue(_should_preserve("desktop.ini"))

    def test_egg_info(self):
        self.assertTrue(_should_preserve("lightwarp.egg-info/PKG-INFO"))

    def test_swap_file(self):
        self.assertTrue(_should_preserve("config/__init__.py.swp"))

    def test_dist_directory(self):
        self.assertTrue(_should_preserve("dist/lightwarp-0.1.0.tar.gz"))

    def test_build_directory(self):
        self.assertTrue(_should_preserve("build/lib/lightwarp/__init__.py"))

    def test_tracked_python_file_not_preserved(self):
        self.assertFalse(_should_preserve("lightwarp/env.py"))

    def test_tracked_readme_not_preserved(self):
        self.assertFalse(_should_preserve("README.md"))

    def test_tracked_bat_not_preserved(self):
        self.assertFalse(_should_preserve("launchers/proj_folders_gui.bat"))

    def test_nested_config_file_not_preserved(self):
        self.assertFalse(_should_preserve("config/structures.py"))


class TestWalkTarget(unittest.TestCase):
    def test_finds_all_files(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("a")
            (root / "sub").mkdir()
            (root / "sub" / "b.txt").write_text("b")
            result = _walk_target(root)
            self.assertEqual(result, {"a.txt", "sub/b.txt"})

    def test_ignores_directories(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "empty_dir").mkdir()
            (root / "file.txt").write_text("x")
            result = _walk_target(root)
            self.assertEqual(result, {"file.txt"})

    def test_empty_directory(self):
        with TemporaryDirectory() as tmp:
            result = _walk_target(Path(tmp))
            self.assertEqual(result, set())


class TestRemoveEmptyDirs(unittest.TestCase):
    def test_removes_empty_leaf_directory(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            empty = root / "a" / "b" / "c"
            empty.mkdir(parents=True)
            _remove_empty_dirs(root)
            self.assertFalse((root / "a").exists())

    def test_preserves_directories_with_files(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "keep").mkdir()
            (root / "keep" / "file.txt").write_text("data")
            (root / "keep" / "empty_child").mkdir()
            _remove_empty_dirs(root)
            self.assertTrue((root / "keep").is_dir())
            self.assertTrue((root / "keep" / "file.txt").is_file())
            self.assertFalse((root / "keep" / "empty_child").exists())

    def test_noop_on_empty_root(self):
        with TemporaryDirectory() as tmp:
            _remove_empty_dirs(Path(tmp))


if __name__ == "__main__":
    unittest.main()
