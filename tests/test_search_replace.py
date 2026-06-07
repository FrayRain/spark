"""Tests for tools/search_replace.py — pattern replacement with dry-run."""
import tempfile
from pathlib import Path
import pytest
from fluxlite.tools.search_replace import search_replace_handler


class TestSearchReplace:
    def test_basic_replace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / "test.txt"
            f.write_text("hello world")
            result = search_replace_handler("hello", "goodbye", path=str(root))
            assert f.read_text() == "goodbye world"
            assert "test.txt" in result

    def test_dry_run_does_not_modify(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / "test.txt"
            f.write_text("hello world")
            result = search_replace_handler("hello", "goodbye", path=str(root), dry_run=True)
            assert f.read_text() == "hello world"  # unchanged
            assert "DRY RUN" in result.upper() or "dry" in result.lower()

    def test_glob_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_text("hello world")
            (root / "b.txt").write_text("hello world")
            result = search_replace_handler("hello", "hi", glob="*.py", path=str(root))
            assert "a.py" in result
            assert "b.txt" not in result

    def test_no_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / "test.txt"
            f.write_text("hello world")
            result = search_replace_handler("nonexistent", "replacement", path=str(root))
            assert "nonexistent" in result.lower() or "no match" in result.lower() or "srch_no_matches" in result

    def test_skips_hidden_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            (root / ".git" / "config").write_text("hello world")
            (root / "src").mkdir()
            (root / "src" / "main.txt").write_text("hello world")
            result = search_replace_handler("hello", "hi", path=str(root))
            assert ".git" not in result
            assert "main.txt" in result or "src" in result

    def test_not_a_directory(self):
        result = search_replace_handler("hello", "hi", path="/nonexistent_dir_98765")
        assert "not a directory" in result.lower() or "nonexistent_dir_98765" in result

    def test_multi_file_replace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("hello")
            (root / "b.txt").write_text("hello")
            result = search_replace_handler("hello", "hi", path=str(root))
            assert "a.txt" in result
            assert "b.txt" in result
            assert root.glob("a.txt").__next__().read_text() == "hi"

    def test_multiple_occurrences(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / "test.txt"
            f.write_text("hello hello world")
            result = search_replace_handler("hello", "hi", path=str(root))
            assert f.read_text() == "hi hi world"
            assert "2 occurrence" in result
