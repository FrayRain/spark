"""Additional tests for enhanced search_replace features (regex, fuzzy, context)."""
import tempfile
from pathlib import Path
from fluxlite.tools.search_replace import search_replace_handler


class TestSearchReplaceFuzzy:
    def test_fuzzy_match_similar_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp, "test.py")
            f.write_text("def calculate_sum(a, b):\n    return a + b\n", encoding="utf-8")
            result = search_replace_handler(
                pattern="def calculate_sum(a, b):",
                replacement="def calculate_sum(x, y):",
                path=tmp,
                fuzzy=True,
                dry_run=True,
            )
            assert "test.py" in result
            assert "1" in result  # at least 1 match

    def test_fuzzy_actual_replace(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp, "test.py")
            f.write_text("def old_func(x):\n    pass\n", encoding="utf-8")
            result = search_replace_handler(
                pattern="def old_func(x):",
                replacement="def new_func(x):",
                path=tmp,
                fuzzy=True,
            )
            assert "1 occurrence" in result
            content = f.read_text()
            assert "def new_func(x):" in content
            assert "old_func" not in content

    def test_fuzzy_no_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp, "test.py")
            f.write_text("completely different content\n", encoding="utf-8")
            result = search_replace_handler(
                pattern="nonexistent pattern xyz",
                replacement="replacement",
                path=tmp,
                fuzzy=True,
            )
            assert "No matches found" in result


class TestSearchReplaceRegex:
    def test_regex_basic(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp, "test.py")
            f.write_text("x = 42\ny = 73\nz = 99\n", encoding="utf-8")
            result = search_replace_handler(
                pattern=r"= \d+",
                replacement="= 0",
                path=tmp,
                regex=True,
                dry_run=True,
            )
            assert "3 occurrences" in result or "test.py" in result
            assert "No matches" not in result

    def test_regex_actual_replace(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp, "test.py")
            f.write_text("foo_bar = 1\nfoo_baz = 2\n", encoding="utf-8")
            result = search_replace_handler(
                pattern=r"foo_\w+",
                replacement="qux",
                path=tmp,
                regex=True,
            )
            assert "2 occurrences" in result or "2" in result
            content = f.read_text()
            assert "qux = 1" in content
            assert "qux = 2" in content

    def test_regex_invalid_pattern(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp, "test.py")
            f.write_text("hello\n", encoding="utf-8")
            result = search_replace_handler(
                pattern=r"[invalid",
                replacement="x",
                path=tmp,
                regex=True,
            )
            assert "error" in result.lower() or "No matches" in result


class TestSearchReplaceContext:
    def test_context_lines_in_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp, "test.py")
            f.write_text("line1\nline2\nline3\ntarget line\nline5\nline6\nline7\n", encoding="utf-8")
            result = search_replace_handler(
                pattern="target line",
                replacement="replaced line",
                path=tmp,
                dry_run=True,
                context_lines=1,
            )
            assert "test.py" in result
            assert "line2" in result or "line3" in result or "line5" in result

    def test_context_zero_no_extra(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp, "test.py")
            f.write_text("a\nb\ntarget\nc\nd\n", encoding="utf-8")
            result = search_replace_handler(
                pattern="target",
                replacement="done",
                path=tmp,
                dry_run=True,
                context_lines=0,
            )
            assert "test.py" in result
            assert "occurrence" in result


class TestSearchReplaceExact:
    def test_exact_still_works(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp, "test.txt")
            f.write_text("hello world\n", encoding="utf-8")
            result = search_replace_handler(
                pattern="hello world",
                replacement="goodbye world",
                path=tmp,
            )
            assert "1 occurrence" in result
            assert f.read_text() == "goodbye world\n"

    def test_exact_multi_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ["a.txt", "b.txt"]:
                Path(tmp, name).write_text("old content\n", encoding="utf-8")
            result = search_replace_handler(
                pattern="old content",
                replacement="new content",
                path=tmp,
            )
            assert "2 files" in result
            for name in ["a.txt", "b.txt"]:
                assert Path(tmp, name).read_text() == "new content\n"
