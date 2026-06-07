import pytest
from fluxlite.context import build_project_tree, build_git_context


class TestProjectTree:
    def test_returns_string(self):
        result = build_project_tree()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_respects_depth(self):
        deep = build_project_tree(max_depth=0)
        shallow = build_project_tree(max_depth=2)
        assert len(deep.split("\n")) <= len(shallow.split("\n"))


class TestGitContext:
    def test_returns_string(self):
        result = build_git_context()
        assert isinstance(result, str)


class TestTokenEstimate:
    def test_empty(self):
        from fluxlite.commands import estimate_tokens
        assert estimate_tokens("") == 0

    def test_english(self):
        from fluxlite.commands import estimate_tokens
        tokens = estimate_tokens("hello world this is a test")
        assert tokens > 0
        assert tokens < 10  # should be roughly 5-6 tokens

    def test_chinese(self):
        from fluxlite.commands import estimate_tokens
        tokens = estimate_tokens("你好世界这是一个测试")
        assert tokens > 0
        # CJK chars: tiktoken counts ~1 token each, fallback ~2
        assert 5 <= tokens <= 25

    def test_mixed(self):
        from fluxlite.commands import estimate_tokens
        tokens = estimate_tokens("hello 你好 world 世界")
        assert tokens > 0

    def test_long_text(self):
        from fluxlite.commands import estimate_tokens
        text = "hello " * 1000
        tokens = estimate_tokens(text)
        assert tokens > 100  # not just 1


class TestBuildFluxliteMd:
    def test_reads_existing(self, monkeypatch, tmp_path):
        f = tmp_path / "FLUXLITE.md"
        f.write_text("test fluxlite content")
        monkeypatch.chdir(tmp_path)
        from fluxlite.context import build_fluxlite_md
        result = build_fluxlite_md()
        assert "test fluxlite content" in result

    def test_not_found(self, monkeypatch, tmp_path):
        monkeypatch.chdir(tmp_path)
        from fluxlite.context import build_fluxlite_md
        assert build_fluxlite_md() == ""

    def test_reads_from_dot_fluxlite(self, monkeypatch, tmp_path):
        (tmp_path / ".fluxlite").mkdir()
        (tmp_path / ".fluxlite" / "FLUXLITE.md").write_text("dotflux content")
        monkeypatch.chdir(tmp_path)
        from fluxlite.context import build_fluxlite_md
        result = build_fluxlite_md()
        assert "dotflux content" in result


class TestBuildProjectMemory:
    def test_reads_existing(self, monkeypatch, tmp_path):
        (tmp_path / ".fluxlite").mkdir()
        (tmp_path / ".fluxlite" / "project_memory.md").write_text("project memory content")
        monkeypatch.chdir(tmp_path)
        from fluxlite.context import build_project_memory
        result = build_project_memory()
        assert "project memory content" in result

    def test_not_found(self, monkeypatch, tmp_path):
        monkeypatch.chdir(tmp_path)
        from fluxlite.context import build_project_memory
        assert build_project_memory() == ""


class TestBuildInstructionsMd:
    def test_reads_instructions_md(self, monkeypatch, tmp_path):
        f = tmp_path / "INSTRUCTIONS.md"
        f.write_text("instructions content")
        monkeypatch.chdir(tmp_path)
        from fluxlite.context import build_instructions_md
        result = build_instructions_md()
        assert "instructions content" in result

    def test_not_found(self, monkeypatch, tmp_path):
        monkeypatch.chdir(tmp_path)
        from fluxlite.context import build_instructions_md
        assert build_instructions_md() == ""

    def test_reads_from_dot_fluxlite(self, monkeypatch, tmp_path):
        (tmp_path / ".fluxlite").mkdir()
        (tmp_path / ".fluxlite" / "instructions.md").write_text("dot instructions")
        monkeypatch.chdir(tmp_path)
        from fluxlite.context import build_instructions_md
        result = build_instructions_md()
        assert "dot instructions" in result


class TestBuildProjectTreeExtended:
    def test_skips_excluded_dirs(self, monkeypatch, tmp_path):
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("")
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "ignore_me.js").write_text("")
        monkeypatch.chdir(tmp_path)
        from fluxlite.context import build_project_tree, PROJECT_TREE_SKIP
        result = build_project_tree(max_depth=3)
        assert "src" in result
        assert "node_modules" not in result

    def test_skips_hidden_dirs(self, monkeypatch, tmp_path):
        (tmp_path / ".hidden_dir").mkdir()
        (tmp_path / ".hidden_dir" / "file.py").write_text("")
        monkeypatch.chdir(tmp_path)
        from fluxlite.context import build_project_tree
        result = build_project_tree(max_depth=3)
        assert ".hidden_dir" not in result

    def test_empty_directory(self, monkeypatch, tmp_path):
        monkeypatch.chdir(tmp_path)
        from fluxlite.context import build_project_tree
        result = build_project_tree(max_depth=3)
        # Should at least contain the directory name
        assert isinstance(result, str)


class TestBuildGitContextExtended:
    def test_returns_branch(self):
        from fluxlite.context import build_git_context
        result = build_git_context()
        assert isinstance(result, str)
        # We're in a git repo, so should contain branch info
        if result:
            assert "Branch:" in result or "branch" in result.lower() or "Status" in result

    def test_not_in_git_repo(self, monkeypatch, tmp_path):
        monkeypatch.chdir(tmp_path)
        from fluxlite.context import build_git_context
        result = build_git_context()
        assert result == ""
