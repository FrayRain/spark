"""Tests for project rules (SPARK.md) module."""
import os
import tempfile
from pathlib import Path
from fluxlite.project_rules import find_rules_file, load_rules, format_rules_block


class TestFindRulesFile:
    def test_no_rules_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = find_rules_file(tmp)
            assert result is None

    def test_finds_spark_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "SPARK.md").write_text("rules", encoding="utf-8")
            result = find_rules_file(tmp)
            assert result is not None
            assert result.name == "SPARK.md"

    def test_finds_dot_sparkrules(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, ".sparkrules").write_text("rules", encoding="utf-8")
            result = find_rules_file(tmp)
            assert result is not None
            assert result.name == ".sparkrules"

    def test_walks_up_parent_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            sub = Path(tmp, "subdir", "nested")
            sub.mkdir(parents=True)
            Path(tmp, "SPARK.md").write_text("rules", encoding="utf-8")
            result = find_rules_file(str(sub))
            assert result is not None
            assert result.name == "SPARK.md"

    def test_prefers_nearest_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            sub = Path(tmp, "subdir")
            sub.mkdir()
            Path(tmp, "SPARK.md").write_text("root rules", encoding="utf-8")
            Path(sub, "SPARK.md").write_text("sub rules", encoding="utf-8")
            result = find_rules_file(str(sub))
            assert result is not None
            assert "sub" in result.read_text()


class TestLoadRules:
    def test_loads_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "SPARK.md").write_text("# My Rules\n- use tabs", encoding="utf-8")
            content = load_rules(tmp)
            assert content is not None
            assert "My Rules" in content
            assert "use tabs" in content

    def test_returns_none_if_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "SPARK.md").write_text("   ", encoding="utf-8")
            content = load_rules(tmp)
            assert content is None

    def test_returns_none_if_no_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            content = load_rules(tmp)
            assert content is None

    def test_handles_unicode(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "SPARK.md").write_text("使用中文规则", encoding="utf-8")
            content = load_rules(tmp)
            assert content == "使用中文规则"


class TestFormatRulesBlock:
    def test_zh_format(self):
        result = format_rules_block("use tabs", lang="zh")
        assert "项目规则" in result
        assert "use tabs" in result

    def test_en_format(self):
        result = format_rules_block("use tabs", lang="en")
        assert "Project Rules" in result
        assert "use tabs" in result

    def test_default_zh(self):
        result = format_rules_block("some rule")
        assert "项目规则" in result
