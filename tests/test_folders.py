"""
Unit tests for lightwarp.folders — the generic folder-spec engine.

Run from the pipeline/ directory:
    python -m pytest tests/
  or:
    python -m unittest discover tests/
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from lightwarp.folders import (
    FolderSpec,
    PipelineNoChangesError,
    PipelinePathExistsError,
    collect_missing_dirs,
    ensure_dirs_from_spec,
    ensure_existing_dir,
    raise_exists,
)

SAMPLE_SPEC: FolderSpec = {
    "alpha": {"sub_a": {}, "sub_b": {}},
    "beta": {},
    "gamma": {"deep": {"deeper": {}}},
}


class TestEnsureDirsFromSpec(unittest.TestCase):
    def test_creates_all_directories(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            root.mkdir()
            created = ensure_dirs_from_spec(root, SAMPLE_SPEC)
            self.assertGreater(len(created), 0)
            self.assertTrue((root / "alpha" / "sub_a").is_dir())
            self.assertTrue((root / "alpha" / "sub_b").is_dir())
            self.assertTrue((root / "beta").is_dir())
            self.assertTrue((root / "gamma" / "deep" / "deeper").is_dir())

    def test_returns_empty_when_all_exist(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            root.mkdir()
            ensure_dirs_from_spec(root, SAMPLE_SPEC)
            created = ensure_dirs_from_spec(root, SAMPLE_SPEC)
            self.assertEqual(created, [])


class TestCollectMissingDirs(unittest.TestCase):
    def test_all_missing_before_creation(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            missing = collect_missing_dirs(root, SAMPLE_SPEC)
            self.assertGreater(len(missing), 0)
            for p in missing:
                self.assertFalse(p.exists())

    def test_none_missing_after_creation(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            root.mkdir()
            ensure_dirs_from_spec(root, SAMPLE_SPEC)
            missing = collect_missing_dirs(root, SAMPLE_SPEC)
            self.assertEqual(missing, [])


class TestEnsureExistingDir(unittest.TestCase):
    def test_passes_for_real_directory(self):
        with TemporaryDirectory() as tmp:
            ensure_existing_dir(Path(tmp), "test dir")

    def test_raises_for_nonexistent(self):
        with self.assertRaises(FileNotFoundError):
            ensure_existing_dir(Path("/nonexistent_dir_xyz"), "test dir")


class TestRaiseExists(unittest.TestCase):
    def test_raises_pipeline_path_exists_error(self):
        with self.assertRaises(PipelinePathExistsError):
            raise_exists("Thing", "foo", Path("/some/path"))


class TestExceptions(unittest.TestCase):
    def test_path_exists_is_file_exists_error(self):
        self.assertTrue(issubclass(PipelinePathExistsError, FileExistsError))

    def test_no_changes_is_exception(self):
        self.assertTrue(issubclass(PipelineNoChangesError, Exception))


if __name__ == "__main__":
    unittest.main()
