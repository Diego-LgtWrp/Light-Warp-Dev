"""
Unit tests for utils.dev.secure_transfer.core — file copy and SHA-256 validation.

Run from the pipeline/ directory:
    python -m pytest tests/test_secure_transfer.py
"""

import hashlib
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from utils.dev.secure_transfer.core import BUFFER_SIZE, copy_file, hash_file, validate_files

SAMPLE_DATA = b"LightWarp pipeline test content\n" * 100


class TestHashFile(unittest.TestCase):
    def test_matches_known_sha256(self):
        expected = hashlib.sha256(SAMPLE_DATA).hexdigest()
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "sample.bin"
            p.write_bytes(SAMPLE_DATA)
            self.assertEqual(hash_file(str(p)), expected)

    def test_empty_file(self):
        expected = hashlib.sha256(b"").hexdigest()
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "empty.bin"
            p.write_bytes(b"")
            self.assertEqual(hash_file(str(p)), expected)

    def test_progress_callback_is_called(self):
        calls = []
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "sample.bin"
            p.write_bytes(SAMPLE_DATA)
            hash_file(str(p), progress_callback=lambda pct: calls.append(pct))
        self.assertGreater(len(calls), 0)
        self.assertAlmostEqual(calls[-1], 1.0, places=2)


class TestCopyFile(unittest.TestCase):
    def test_copies_content_correctly(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "source.bin"
            dst = Path(tmp) / "dest.bin"
            src.write_bytes(SAMPLE_DATA)
            copy_file(str(src), str(dst))
            self.assertEqual(dst.read_bytes(), SAMPLE_DATA)

    def test_raises_on_same_path(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "file.bin"
            src.write_bytes(b"data")
            with self.assertRaises(ValueError):
                copy_file(str(src), str(src))

    def test_raises_if_destination_exists(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "source.bin"
            dst = Path(tmp) / "dest.bin"
            src.write_bytes(b"data")
            dst.write_bytes(b"existing")
            with self.assertRaises(FileExistsError):
                copy_file(str(src), str(dst))

    def test_progress_callback_is_called(self):
        calls = []
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "source.bin"
            dst = Path(tmp) / "dest.bin"
            src.write_bytes(SAMPLE_DATA)
            copy_file(str(src), str(dst), progress_callback=lambda pct: calls.append(pct))
        self.assertGreater(len(calls), 0)


class TestValidateFiles(unittest.TestCase):
    def test_identical_files_return_true(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "a.bin"
            dst = Path(tmp) / "b.bin"
            src.write_bytes(SAMPLE_DATA)
            dst.write_bytes(SAMPLE_DATA)
            self.assertTrue(validate_files(str(src), str(dst)))

    def test_different_files_return_false(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "a.bin"
            dst = Path(tmp) / "b.bin"
            src.write_bytes(b"hello")
            dst.write_bytes(b"world")
            self.assertFalse(validate_files(str(src), str(dst)))

    def test_same_path_returns_false(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "a.bin"
            src.write_bytes(b"data")
            self.assertFalse(validate_files(str(src), str(src)))

    def test_different_sizes_return_false(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "a.bin"
            dst = Path(tmp) / "b.bin"
            src.write_bytes(b"short")
            dst.write_bytes(b"longer content here")
            self.assertFalse(validate_files(str(src), str(dst)))


if __name__ == "__main__":
    unittest.main()
