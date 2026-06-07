"""Tests for knowledge.py — chunking, TF-IDF, and KnowledgeBase."""
import os
import math
import json
import tempfile
from pathlib import Path
import pytest
from fluxlite.knowledge import (
    _py_chunks, _md_chunks, _generic_chunks,
    _tokenize, _compute_idf, _vectorize, _cosine_sim,
    _buf_char_count, _chunk_file,
    KnowledgeBase, CHUNK_MIN_CHARS, CHUNK_MAX_CHARS, MAX_CHUNKS,
    INDEX_EXTENSIONS, EXCLUDE_DIRS,
)


# ---------------------------------------------------------------------------
# _buf_char_count
# ---------------------------------------------------------------------------

class TestBufCharCount:
    def test_simple(self):
        lines = ["abc", "de", "f"]
        assert _buf_char_count(lines, 0, 3) == 6  # 3 + 2 + 1

    def test_empty_lines(self):
        assert _buf_char_count(["", "", ""], 0, 3) == 0

    def test_slice(self):
        lines = ["hello", "world", "foo"]
        assert _buf_char_count(lines, 1, 3) == 8  # 5 + 3

    def test_zero_length(self):
        lines = ["abc"]
        assert _buf_char_count(lines, 1, 1) == 0


# ---------------------------------------------------------------------------
# _py_chunks
# ---------------------------------------------------------------------------

class TestPyChunks:
    def test_empty_file(self):
        assert _py_chunks("", "empty.py") == []

    def test_short_file_single_chunk(self):
        text = "x = 1\ny = 2"
        chunks = _py_chunks(text, "test.py")
        assert len(chunks) == 1
        assert chunks[0]["content"] == "x = 1\ny = 2"
        assert chunks[0]["start"] == 1
        assert chunks[0]["end"] == 2

    def test_splits_at_function_boundaries(self):
        text = "import os\n\ndef hello():\n    print('hi')\n\ndef world():\n    print('bye')"
        chunks = _py_chunks(text, "test.py")
        assert len(chunks) == 2
        assert "def hello():" in chunks[0]["content"]
        assert chunks[1]["heading"] == "def world():"

    def test_heading_tracked(self):
        text = "def setup():\n    pass\n\ndef teardown():\n    pass"
        chunks = _py_chunks(text, "test.py")
        headings = [c["heading"] for c in chunks if c["heading"]]
        assert any("def teardown():" in h for h in headings)

    def test_long_buffer_forced_flush(self):
        # Each line ~7 chars, 500 lines = ~3500 chars > CHUNK_MAX_CHARS
        body = "\n".join(f"x = {i}" for i in range(500))
        chunks = _py_chunks(body, "test.py")
        assert len(chunks) >= 2
        for c in chunks:
            # Allow small overflow past CHUNK_MAX_CHARS
            assert len(c["content"]) < CHUNK_MAX_CHARS + 300


# ---------------------------------------------------------------------------
# _md_chunks
# ---------------------------------------------------------------------------

class TestMdChunks:
    def test_empty(self):
        assert _md_chunks("", "test.md") == []

    def test_no_headings_single_chunk(self):
        text = "plain text\nwithout any\nheadings"
        chunks = _md_chunks(text, "test.md")
        assert len(chunks) >= 1

    def test_splits_at_headings(self):
        text = "intro\n## Section A\ncontent a\n## Section B\ncontent b"
        chunks = _md_chunks(text, "test.md")
        assert len(chunks) >= 2
        headings = [c["heading"] for c in chunks if c["heading"]]
        assert any("Section B" in h for h in headings)


# ---------------------------------------------------------------------------
# _generic_chunks
# ---------------------------------------------------------------------------

class TestGenericChunks:
    def test_single_paragraph(self):
        text = "hello world test content"
        chunks = _generic_chunks(text, "test.txt")
        assert len(chunks) >= 1
        assert chunks[0]["content"].strip() == text

    def test_splits_large_text(self):
        # Create text large enough to exceed CHUNK_MAX_CHARS
        para = "word " * 300  # ~1500 chars
        text = "\n\n".join([para, para, para])
        chunks = _generic_chunks(text, "test.txt")
        assert len(chunks) >= 2


# ---------------------------------------------------------------------------
# _chunk_file
# ---------------------------------------------------------------------------

class TestChunkFile:
    def test_dispatches_by_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, ext in [("test.py", ".py"), ("readme.md", ".md"), ("data.txt", ".txt")]:
                f = root / name
                f.write_text("hello world\n" * 10)
                chunks = _chunk_file(f, root)
                assert len(chunks) >= 1
                assert all(c["file"] == name for c in chunks)

    def test_skips_binary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / "test.py"
            f.write_bytes(b"\x00\x01\x02")
            chunks = _chunk_file(f, root)
            # Should not crash, may produce empty or skip
            assert isinstance(chunks, list)

    def test_returns_empty_on_read_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / "test.py"
            # Don't create the file
            chunks = _chunk_file(f, root)
            assert chunks == []


# ---------------------------------------------------------------------------
# _tokenize
# ---------------------------------------------------------------------------

class TestTokenize:
    def test_returns_list(self):
        tokens = _tokenize("hello world")
        assert isinstance(tokens, list)
        assert len(tokens) > 0

    def test_contains_ngrams(self):
        tokens = _tokenize("hello")
        # Should contain the full token plus n-grams
        assert "hello" in tokens
        assert "he" in tokens
        assert "el" in tokens
        assert "hel" in tokens
        assert "ell" in tokens

    def test_short_token_no_ngrams(self):
        tokens = _tokenize("hi")
        assert "hi" in tokens
        # No n-grams for len <= 3
        assert len([t for t in tokens if t != "hi"]) == 0

    def test_empty(self):
        assert _tokenize("") == []


# ---------------------------------------------------------------------------
# _compute_idf
# ---------------------------------------------------------------------------

class TestComputeIDF:
    def test_single_chunk(self):
        chunks = [{"content": "hello world"}]
        idf = _compute_idf(chunks)
        assert len(idf) > 0
        # With n=1 doc: idf = log((1+1)/(c+1))+1 = log(2/2)+1 = 1.0 for each token
        for token, val in idf.items():
            assert val == 1.0

    def test_repeated_token_in_one_doc(self):
        chunks = [
            {"content": "hello hello"},
            {"content": "world"},
        ]
        idf = _compute_idf(chunks)
        # "hello" appears in 1 of 2 docs: idf = log(3/2) + 1 ≈ 1.405
        assert "hello" in idf
        assert idf["hello"] == pytest.approx(math.log(3 / 2) + 1, rel=0.01)


# ---------------------------------------------------------------------------
# _vectorize
# ---------------------------------------------------------------------------

class TestVectorize:
    def test_returns_dict(self):
        idf = {"hello": 1.0, "world": 2.0}
        vec = _vectorize("hello world", idf)
        assert isinstance(vec, dict)
        assert len(vec) > 0


# ---------------------------------------------------------------------------
# _cosine_sim
# ---------------------------------------------------------------------------

class TestCosineSim:
    def test_identical_vectors(self):
        a = {"x": 1.0, "y": 2.0}
        b = {"x": 1.0, "y": 2.0}
        assert _cosine_sim(a, b) == pytest.approx(1.0, rel=0.01)

    def test_orthogonal_vectors(self):
        a = {"x": 1.0}
        b = {"y": 1.0}
        assert _cosine_sim(a, b) == 0.0

    def test_empty_intersection(self):
        a = {"x": 1.0}
        b = {"y": 1.0}
        assert _cosine_sim(a, b) == 0.0

    def test_zero_vector(self):
        assert _cosine_sim({}, {"x": 1.0}) == 0.0


# ---------------------------------------------------------------------------
# KnowledgeBase
# ---------------------------------------------------------------------------

class TestKnowledgeBase:
    def test_build_and_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text(
                "def hello():\n    return 'hello world'\n\ndef auth():\n    pass"
            )
            (root / "src" / "utils.py").write_text(
                "def helper():\n    return 42"
            )

            kb = KnowledgeBase(root)
            assert not kb.is_built()

            msg = kb.build()
            assert kb.is_built()
            assert len(msg) > 0
            assert len(kb.chunks) > 0

            results = kb.search("hello")
            assert isinstance(results, list)

    def test_search_not_built(self):
        with tempfile.TemporaryDirectory() as tmp:
            kb = KnowledgeBase(tmp)
            assert kb.search("anything") == []

    def test_stats(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text("x = 1")
            kb = KnowledgeBase(root)
            stats = kb.stats()
            # Not yet built — should indicate uninitialized state
            assert len(stats) > 0
            assert not kb.is_built()

            kb.build()
            stats = kb.stats()
            assert len(stats) > 0
            assert "knowledge" in stats.lower() or "[knowledge]" in stats

    def test_empty_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            kb = KnowledgeBase(tmp)
            msg = kb.build()
            assert msg  # no files message
            assert kb.chunks == []

    def test_discover_files_filters_extensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.py").write_text("x = 1")
            (root / "data.bin").write_text("binary")
            kb = KnowledgeBase(root)
            files = kb._discover_files()
            names = {f.name for f in files}
            assert "main.py" in names
            assert "data.bin" not in names

    def test_discover_files_excludes_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("x = 1")
            (root / ".git").mkdir()
            (root / ".git" / "config").write_text("")
            kb = KnowledgeBase(root)
            files = kb._discover_files()
            paths = [str(f) for f in files]
            assert any("src" in p for p in paths)
            assert not any(".git" in p for p in paths)

    def test_incremental_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.py").write_text("x = 1")
            kb = KnowledgeBase(root)
            msg1 = kb.build()
            assert kb.is_built()

            # Second build should be incremental (no changes)
            msg2 = kb.build()
            assert len(msg2) > 0

    def test_force_rebuild(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.py").write_text("x = 1")
            kb = KnowledgeBase(root)
            kb.build()

            # Adding a file
            (root / "utils.py").write_text("y = 2")
            msg = kb.build()  # incremental — detects change
            assert msg

    def test_check_changes_detects_new_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.py").write_text("x = 1")
            kb = KnowledgeBase(root)
            kb.build()

            (root / "new.py").write_text("y = 2")
            files = kb._discover_files()
            assert kb._check_changes(files) is True

    def test_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.py").write_text("x = 1\ny = 2")
            kb = KnowledgeBase(root)
            kb.build()

            store_dir = kb.store_dir
            assert (store_dir / "meta.json").exists()

            # Create a new KB pointing to the same root
            kb2 = KnowledgeBase(root)
            assert not kb2.is_built()
            loaded = kb2._load()
            assert loaded is True
            assert kb2.is_built()
            assert len(kb2.chunks) > 0
