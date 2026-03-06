"""
Unit tests for tools.proj_folders.core — project/asset/shot builders.

Run from the pipeline/ directory:
    python -m pytest tests/
  or:
    python -m unittest discover tests/
"""

import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from config import ASSET_STRUCTURE, PROJECT_STRUCTURE, RENDER_STRUCTURE, SHOT_STRUCTURE, ASSET_TYPES
from lightwarp.folders import PipelineNoChangesError, PipelinePathExistsError, collect_missing_dirs
from tools.proj_folders.core import (
    create_asset_structure,
    create_project_structure,
    create_shot_structure,
    preview_asset_structure,
    preview_project_structure,
    preview_shot_structure,
    preview_update_asset_structure,
    preview_update_project_structure,
    preview_update_shot_structure,
    update_asset_structure,
    update_project_structure,
    update_shot_structure,
)


class TestCreateProject(unittest.TestCase):
    def test_creates_all_top_level_folders(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = create_project_structure(root, "TestFilm")
            self.assertEqual(result, root / "TestFilm")
            for folder in PROJECT_STRUCTURE:
                self.assertTrue((result / folder).is_dir(), f"Missing: {folder}")

    def test_raises_if_project_already_exists(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_project_structure(root, "TestFilm")
            with self.assertRaises(PipelinePathExistsError):
                create_project_structure(root, "TestFilm")

    def test_creates_nested_folders(self):
        with TemporaryDirectory() as tmp:
            result = create_project_structure(Path(tmp), "TestFilm")
            self.assertTrue((result / "utils" / "vdev").is_dir())
            self.assertTrue((result / "utils" / "tools").is_dir())
            self.assertTrue((result / "final" / "edit").is_dir())


class TestUpdateProject(unittest.TestCase):
    def test_raises_if_project_missing(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                update_project_structure(Path(tmp) / "NonExistent")

    def test_raises_no_changes_when_already_up_to_date(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project_root = create_project_structure(root, "TestFilm")
            with self.assertRaises(PipelineNoChangesError):
                update_project_structure(project_root)

    def test_adds_only_missing_folders(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project_root = create_project_structure(root, "TestFilm")
            shutil.rmtree(project_root / "unreal")
            result = update_project_structure(project_root)
            self.assertEqual(result, project_root)
            self.assertTrue((project_root / "unreal").is_dir())


class TestPreviewProject(unittest.TestCase):
    def test_preview_returns_all_paths_without_creating(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = preview_project_structure(root, "TestFilm")
            self.assertGreater(len(missing), 0)
            self.assertFalse((root / "TestFilm").exists())

    def test_preview_raises_if_project_exists(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_project_structure(root, "TestFilm")
            with self.assertRaises(PipelinePathExistsError):
                preview_project_structure(root, "TestFilm")

    def test_preview_update_returns_empty_when_up_to_date(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project_root = create_project_structure(root, "TestFilm")
            missing = preview_update_project_structure(project_root)
            self.assertEqual(missing, [])


class TestCreateAsset(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.project_root = create_project_structure(Path(self._tmp.name), "TestFilm")

    def tearDown(self):
        self._tmp.cleanup()

    def test_creates_all_asset_folders(self):
        result = create_asset_structure(self.project_root, "char_hero")
        self.assertEqual(result, self.project_root / "asset" / "char_hero")
        for folder in ASSET_STRUCTURE:
            self.assertTrue((result / folder).is_dir(), f"Missing: {folder}")

    def test_raises_if_asset_exists(self):
        create_asset_structure(self.project_root, "char_hero")
        with self.assertRaises(PipelinePathExistsError):
            create_asset_structure(self.project_root, "char_hero")

    def test_preview_returns_paths_without_creating(self):
        missing = preview_asset_structure(self.project_root, "char_hero")
        self.assertGreater(len(missing), 0)
        self.assertFalse((self.project_root / "asset" / "char_hero").exists())


class TestUpdateAsset(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.project_root = create_project_structure(Path(self._tmp.name), "TestFilm")
        self.asset_root = create_asset_structure(self.project_root, "char_hero")

    def tearDown(self):
        self._tmp.cleanup()

    def test_raises_if_asset_missing(self):
        with self.assertRaises(FileNotFoundError):
            update_asset_structure(self.project_root, "char_nonexistent")

    def test_raises_no_changes_when_up_to_date(self):
        with self.assertRaises(PipelineNoChangesError):
            update_asset_structure(self.project_root, "char_hero")

    def test_adds_missing_asset_folder(self):
        shutil.rmtree(self.asset_root / "geo")
        result = update_asset_structure(self.project_root, "char_hero")
        self.assertEqual(result, self.asset_root)
        self.assertTrue((self.asset_root / "geo").is_dir())


class TestCreateShot(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.project_root = create_project_structure(Path(self._tmp.name), "TestFilm")

    def tearDown(self):
        self._tmp.cleanup()

    def test_creates_shot_and_render_folders(self):
        shot_root, render_root = create_shot_structure(self.project_root, "sh010")
        self.assertEqual(shot_root, self.project_root / "shot" / "sh010")
        self.assertEqual(render_root, self.project_root / "render" / "sh010")
        for folder in SHOT_STRUCTURE:
            self.assertTrue((shot_root / folder).is_dir(), f"Missing shot folder: {folder}")
        for folder in RENDER_STRUCTURE:
            self.assertTrue((render_root / folder).is_dir(), f"Missing render folder: {folder}")

    def test_raises_if_shot_exists(self):
        create_shot_structure(self.project_root, "sh010")
        with self.assertRaises(PipelinePathExistsError):
            create_shot_structure(self.project_root, "sh010")

    def test_preview_returns_paths_without_creating(self):
        missing_shot, missing_render = preview_shot_structure(self.project_root, "sh010")
        self.assertGreater(len(missing_shot), 0)
        self.assertGreater(len(missing_render), 0)
        self.assertFalse((self.project_root / "shot" / "sh010").exists())


class TestUpdateShot(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.project_root = create_project_structure(Path(self._tmp.name), "TestFilm")
        self.shot_root, self.render_root = create_shot_structure(self.project_root, "sh010")

    def tearDown(self):
        self._tmp.cleanup()

    def test_raises_if_shot_missing(self):
        with self.assertRaises(FileNotFoundError):
            update_shot_structure(self.project_root, "sh_nonexistent")

    def test_raises_no_changes_when_up_to_date(self):
        with self.assertRaises(PipelineNoChangesError):
            update_shot_structure(self.project_root, "sh010")

    def test_preview_update_empty_when_up_to_date(self):
        missing_shot, missing_render = preview_update_shot_structure(self.project_root, "sh010")
        self.assertEqual(missing_shot, [])
        self.assertEqual(missing_render, [])


class TestAssetTypes(unittest.TestCase):
    def test_asset_types_is_a_list_of_strings(self):
        self.assertIsInstance(ASSET_TYPES, list)
        self.assertTrue(all(isinstance(t, str) for t in ASSET_TYPES))
        self.assertGreater(len(ASSET_TYPES), 0)


class TestCollectMissingDirsIntegration(unittest.TestCase):
    def test_returns_empty_when_all_exist(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_project_structure(root, "TestFilm")
            missing = collect_missing_dirs(root / "TestFilm", PROJECT_STRUCTURE)
            self.assertEqual(missing, [])

    def test_returns_missing_paths_before_creation(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = collect_missing_dirs(root / "TestFilm", PROJECT_STRUCTURE)
            self.assertGreater(len(missing), 0)
            for p in missing:
                self.assertFalse(p.exists())


if __name__ == "__main__":
    unittest.main()
