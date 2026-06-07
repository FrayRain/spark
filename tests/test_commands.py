"""Tests for commands.py — pure functions and CommandState."""
from datetime import datetime
from pathlib import Path
import pytest
from fluxlite.commands import (
    perform_rewind, compact_memory, CommandState,
    estimate_tokens,
)


# ---------------------------------------------------------------------------
# estimate_tokens (additional coverage beyond test_context.py)
# ---------------------------------------------------------------------------

class TestEstimateTokens:
    def test_none(self):
        assert estimate_tokens("") == 0

    def test_whitespace(self):
        assert estimate_tokens("   ") > 0

    def test_special_chars(self):
        tokens = estimate_tokens("!@#$%^&*()")
        assert tokens > 0


# ---------------------------------------------------------------------------
# perform_rewind
# ---------------------------------------------------------------------------

class TestPerformRewind:
    def test_rewinds_to_last_user_and_beyond(self):
        msgs = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"},
            {"role": "user", "content": "question"},
            {"role": "assistant", "content": "answer"},
        ]
        result = perform_rewind(msgs)
        assert result is True
        # Removes the last user message AND everything after it
        assert len(msgs) == 2
        assert msgs[-1]["role"] == "assistant"

    def test_no_user_message_returns_false(self):
        msgs = [
            {"role": "assistant", "content": "hello"},
            {"role": "assistant", "content": "world"},
        ]
        result = perform_rewind(msgs)
        assert result is False
        assert len(msgs) == 2

    def test_empty_list(self):
        msgs = []
        result = perform_rewind(msgs)
        assert result is False

    def test_single_user(self):
        msgs = [{"role": "user", "content": "hello"}]
        result = perform_rewind(msgs)
        assert result is True
        assert msgs == []


# ---------------------------------------------------------------------------
# CommandState
# ---------------------------------------------------------------------------

class TestCommandState:
    def setup_method(self):
        CommandState.thinking_mode = "off"
        CommandState.reasoning_effort = ""
        CommandState.auto_debug = True
        CommandState.show_tool_result = False
        CommandState.show_token_usage = False
        CommandState.new_session_requested = False
        CommandState.git_autocommit = False
        CommandState.pinned_files = set()

    def test_defaults(self):
        assert CommandState.thinking_mode == "off"
        assert CommandState.auto_debug is True
        assert CommandState.show_tool_result is False
        assert CommandState.pinned_files == set()

    def test_reset_pins(self):
        CommandState.pinned_files = {"a.py", "b.py"}
        assert len(CommandState.pinned_files) == 2
        CommandState.reset_pins()
        assert CommandState.pinned_files == set()

    def test_settings_keys_match(self):
        expected = {
            "thinking_mode", "reasoning_effort", "auto_debug",
            "show_tool_result", "show_token_usage", "git_autocommit",
        }
        assert set(CommandState._SETTINGS_KEYS) == expected


# ---------------------------------------------------------------------------
# compact_memory
# ---------------------------------------------------------------------------

class TestCompactMemory:
    def test_less_than_three_no_op(self, monkeypatch):
        entries = [{"id": "1", "content": "a", "created_at": "now"}]
        monkeypatch.setattr("fluxlite.commands.load_memories", lambda: entries)
        saved = []

        def mock_save(e):
            saved.extend(e)

        monkeypatch.setattr("fluxlite.commands.save_memories", mock_save)
        compact_memory()
        assert len(saved) == 0  # no change

    def test_three_or_more_compacts(self, monkeypatch):
        entries = [
            {"id": "1", "content": "a", "created_at": "now"},
            {"id": "2", "content": "b", "created_at": "now"},
            {"id": "3", "content": "c", "created_at": "now"},
        ]
        monkeypatch.setattr("fluxlite.commands.load_memories", lambda: entries)
        saved = []

        def mock_save(e):
            saved.extend(e)

        monkeypatch.setattr("fluxlite.commands.save_memories", mock_save)
        compact_memory()
        assert len(saved) == 1
        assert saved[0]["id"] == "compact"
        assert "Consolidated memory" in saved[0]["content"]
