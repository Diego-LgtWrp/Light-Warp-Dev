"""
Unit tests for lightwarp.naming — file versioning and naming engine.

Run from the repo root:
    python -m pytest tests/test_naming.py
  or:
    python -m unittest tests.test_naming
"""

import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from lightwarp.naming import (
    format_version,
    latest_version_number,
    latest_version_path,
    list_versions,
    next_version_path,
    parse_version,
    save_next_version,
    version_path,
)


class TestFormatVersion(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(format_version("char_hero", 1, ".blend"), "char_hero_v001.blend")

    def test_high_version(self):
        self.assertEqual(format_version("char_hero", 42, ".blend"), "char_hero_v042.blend")

    def test_different_extension(self):
        self.assertEqual(format_version("sh010_anim", 5, ".usd"), "sh010_anim_v005.usd")

    def test_version_zero(self):
        self.assertEqual(format_version("test", 0, ".txt"), "test_v000.txt")


class TestParseVersion(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(parse_version("char_hero_v001.blend", "char_hero", ".blend"), 1)

    def test_high_version(self):
        self.assertEqual(parse_version("char_hero_v042.blend", "char_hero", ".blend"), 42)

    def test_no_match_wrong_name(self):
        self.assertIsNone(parse_version("prop_sword_v001.blend", "char_hero", ".blend"))

    def test_no_match_wrong_ext(self):
        self.assertIsNone(parse_version("char_hero_v001.spp", "char_hero", ".blend"))

    def test_no_match_no_version(self):
        self.assertIsNone(parse_version("char_hero.blend", "char_hero", ".blend"))

    def test_no_match_garbage(self):
        self.assertIsNone(parse_version("random_file.txt", "char_hero", ".blend"))

    def test_roundtrip(self):
        name = format_version("prop_table", 17, ".fbx")
        self.assertEqual(parse_version(name, "prop_table", ".fbx"), 17)


class TestVersionPath(unittest.TestCase):
    def test_returns_full_path(self):
        d = Path("/projects/MyFilm/asset/char_hero/blend")
        result = version_path(d, "char_hero", 3, ".blend")
        self.assertEqual(result, d / "char_hero_v003.blend")


class TestListVersions(unittest.TestCase):
    def test_empty_directory(self):
        with TemporaryDirectory() as tmp:
            self.assertEqual(list_versions(Path(tmp), "hero", ".blend"), [])

    def test_nonexistent_directory(self):
        self.assertEqual(list_versions(Path("/nonexistent"), "hero", ".blend"), [])

    def test_finds_versions_sorted(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "hero_v003.blend").touch()
            (d / "hero_v001.blend").touch()
            (d / "hero_v002.blend").touch()
            (d / "unrelated.txt").touch()
            result = list_versions(d, "hero", ".blend")
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0][0], 1)
            self.assertEqual(result[1][0], 2)
            self.assertEqual(result[2][0], 3)

    def test_ignores_wrong_name(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "hero_v001.blend").touch()
            (d / "villain_v001.blend").touch()
            result = list_versions(d, "hero", ".blend")
            self.assertEqual(len(result), 1)

    def test_ignores_wrong_extension(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "hero_v001.blend").touch()
            (d / "hero_v001.spp").touch()
            result = list_versions(d, "hero", ".blend")
            self.assertEqual(len(result), 1)

    def test_ignores_directories(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "hero_v001.blend").mkdir()
            result = list_versions(d, "hero", ".blend")
            self.assertEqual(len(result), 0)


class TestLatestVersionPath(unittest.TestCase):
    def test_none_when_empty(self):
        with TemporaryDirectory() as tmp:
            self.assertIsNone(latest_version_path(Path(tmp), "hero", ".blend"))

    def test_returns_highest(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "hero_v001.blend").touch()
            (d / "hero_v005.blend").touch()
            (d / "hero_v003.blend").touch()
            result = latest_version_path(d, "hero", ".blend")
            self.assertEqual(result, d / "hero_v005.blend")


class TestLatestVersionNumber(unittest.TestCase):
    def test_zero_when_empty(self):
        with TemporaryDirectory() as tmp:
            self.assertEqual(latest_version_number(Path(tmp), "hero", ".blend"), 0)

    def test_returns_highest_number(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "hero_v001.blend").touch()
            (d / "hero_v010.blend").touch()
            self.assertEqual(latest_version_number(d, "hero", ".blend"), 10)


class TestNextVersionPath(unittest.TestCase):
    def test_v001_when_empty(self):
        with TemporaryDirectory() as tmp:
            result = next_version_path(Path(tmp), "hero", ".blend")
            self.assertEqual(result.name, "hero_v001.blend")

    def test_increments(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "hero_v001.blend").touch()
            (d / "hero_v002.blend").touch()
            result = next_version_path(d, "hero", ".blend")
            self.assertEqual(result.name, "hero_v003.blend")

    def test_handles_gaps(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "hero_v001.blend").touch()
            (d / "hero_v005.blend").touch()
            result = next_version_path(d, "hero", ".blend")
            self.assertEqual(result.name, "hero_v006.blend")


class TestSaveNextVersion(unittest.TestCase):
    def test_creates_v001(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "source.blend"
            src.write_bytes(b"blender data")
            dest_dir = Path(tmp) / "output"
            dest_dir.mkdir()
            result = save_next_version(src, dest_dir, "hero")
            self.assertEqual(result.name, "hero_v001.blend")
            self.assertTrue(result.is_file())
            self.assertEqual(result.read_bytes(), b"blender data")

    def test_increments_version(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "source.blend"
            src.write_bytes(b"data")
            dest_dir = Path(tmp) / "output"
            dest_dir.mkdir()
            (dest_dir / "hero_v001.blend").touch()
            (dest_dir / "hero_v002.blend").touch()
            result = save_next_version(src, dest_dir, "hero")
            self.assertEqual(result.name, "hero_v003.blend")

    def test_custom_extension(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "source.blend"
            src.write_bytes(b"data")
            dest_dir = Path(tmp) / "output"
            dest_dir.mkdir()
            result = save_next_version(src, dest_dir, "hero", ext=".abc")
            self.assertEqual(result.name, "hero_v001.abc")

    def test_creates_parent_dirs(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "source.txt"
            src.write_bytes(b"data")
            dest_dir = Path(tmp) / "deep" / "nested" / "dir"
            result = save_next_version(src, dest_dir, "thing")
            self.assertTrue(result.is_file())

    def test_raises_on_missing_source(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                save_next_version(Path(tmp) / "nope.blend", Path(tmp), "hero")


if __name__ == "__main__":
    unittest.main()
