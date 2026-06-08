"""Project rules: load SPARK.md from project root into system context.

Scans the current working directory and parent directories for a SPARK.md
or .sparkrules file. The contents are injected into the system prompt so
the AI can follow project-specific conventions, architecture, and rules.
"""
import os
from pathlib import Path

RULES_FILENAMES = ["SPARK.md", ".sparkrules"]


def find_rules_file(start_dir: str | None = None) -> Path | None:
    """Walk up from start_dir looking for a rules file.

    Searches for SPARK.md or .sparkrules in start_dir, then parent
    directories, up to the filesystem root. Returns the first match.
    """
    if start_dir is None:
        start_dir = os.getcwd()

    current = Path(start_dir).resolve()
    for parent in [current] + list(current.parents):
        for name in RULES_FILENAMES:
            candidate = parent / name
            if candidate.is_file():
                return candidate
    return None


def load_rules(start_dir: str | None = None) -> str | None:
    """Load project rules content if a rules file exists.

    Returns the file content as a string, or None if no rules file found.
    """
    path = find_rules_file(start_dir)
    if path is None:
        return None
    try:
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            return None
        return content
    except (OSError, UnicodeDecodeError):
        return None


def format_rules_block(content: str, lang: str = "zh") -> str:
    """Format rules content for injection into system prompt."""
    if lang == "zh":
        return (
            "\n\n📋 项目规则 (SPARK.md):\n"
            "以下是当前项目的规则说明，请严格遵守：\n"
            f"{content}\n"
        )
    return (
            "\n\n📋 Project Rules (SPARK.md):\n"
            "The project defines the following rules. Follow them strictly:\n"
            f"{content}\n"
    )
