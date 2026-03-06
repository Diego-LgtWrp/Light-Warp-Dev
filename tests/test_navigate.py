"""
Unit tests for lightwarp.navigate — path resolvers, listing, and open helpers.

Run from the pipeline/ directory:
    python -m pytest tests/test_navigate.py
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from lightwarp.navigate import (
    asset_path,
    list_assets,
    list_projects,
    list_shots,
    project_path,
    render_path,
    shot_path,
)


class TestPathResolvers(unittest.TestCase):
    def test_project_path(self):
        root = Path("/studio/projects")
        self.assertEqual(
            project_path("MyFilm", projects_root=root),
            root / "MyFilm",
        )

    def test_asset_path(self):
        root = Path("/studio/projects")
        self.assertEqual(
            asset_path("MyFilm", "char_hero", projects_root=root),
            root / "MyFilm" / "asset" / "char_hero",
        )

    def test_shot_path(self):
        root = Path("/studio/projects")
        self.assertEqual(
            shot_path("MyFilm", "sh010", projects_root=root),
            root / "MyFilm" / "shot" / "sh010",
        )

    def test_render_path(self):
        root = Path("/studio/projects")
        self.assertEqual(
            render_path("MyFilm", "sh010", projects_root=root),
            root / "MyFilm" / "render" / "sh010",
        )


class TestListProjects(unittest.TestCase):
    def test_lists_project_directories(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Alpha").mkdir()
            (root / "Beta").mkdir()
            (root / "not_a_dir.txt").write_text("x")
            result = list_projects(projects_root=root)
            self.assertEqual(result, ["Alpha", "Beta"])

    def test_returns_empty_for_missing_dir(self):
        result = list_projects(projects_root=Path("/nonexistent_xyz"))
        self.assertEqual(result, [])

    def test_returns_sorted(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ["Zulu", "Alpha", "Mike"]:
                (root / name).mkdir()
            self.assertEqual(list_projects(projects_root=root), ["Alpha", "Mike", "Zulu"])


class TestListAssets(unittest.TestCase):
    def test_lists_asset_directories(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "MyFilm"
            asset_dir = project / "asset"
            asset_dir.mkdir(parents=True)
            (asset_dir / "char_hero").mkdir()
            (asset_dir / "prop_sword").mkdir()
            result = list_assets("MyFilm", projects_root=root)
            self.assertEqual(result, ["char_hero", "prop_sword"])

    def test_returns_empty_when_no_assets(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "MyFilm" / "asset").mkdir(parents=True)
            self.assertEqual(list_assets("MyFilm", projects_root=root), [])

    def test_returns_empty_when_project_missing(self):
        self.assertEqual(
            list_assets("NoSuchProject", projects_root=Path("/nonexistent_xyz")),
            [],
        )


class TestListShots(unittest.TestCase):
    def test_lists_shot_directories(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            shot_dir = root / "MyFilm" / "shot"
            shot_dir.mkdir(parents=True)
            (shot_dir / "sh010").mkdir()
            (shot_dir / "sh020").mkdir()
            (shot_dir / "sh005").mkdir()
            result = list_shots("MyFilm", projects_root=root)
            self.assertEqual(result, ["sh005", "sh010", "sh020"])

    def test_returns_empty_when_no_shots(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "MyFilm" / "shot").mkdir(parents=True)
            self.assertEqual(list_shots("MyFilm", projects_root=root), [])


if __name__ == "__main__":
    unittest.main()
