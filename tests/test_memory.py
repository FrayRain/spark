"""Test memory module — current API (memories list, no identity/rules)."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import fluxlite.memory as mem


class TestMemory:
    def _memories(self):
        """Return empty memories list via the module API."""
        return mem.load_memories()

    @patch("fluxlite.memory.MEMORY_PATH", new_callable=lambda: Path(tempfile.mkdtemp()) / "mem.json")
    def test_load_default(self, _):
        entries = self._memories()
        assert isinstance(entries, list)
        assert len(entries) == 0

    @patch("fluxlite.memory.MEMORY_PATH", new_callable=lambda: Path(tempfile.mkdtemp()) / "mem.json")
    def test_save_and_load(self, _):
        mem.save_memories([{"id": "1", "content": "hello", "created_at": "now"}])
        entries = mem.load_memories()
        assert len(entries) == 1
        assert entries[0]["content"] == "hello"

    @patch("fluxlite.memory.MEMORY_PATH", new_callable=lambda: Path(tempfile.mkdtemp()) / "mem.json")
    def test_add_memory(self, _):
        entry = mem.add_memory("User likes Python")
        assert entry["content"] == "User likes Python"
        assert "id" in entry
        assert "created_at" in entry

    @patch("fluxlite.memory.MEMORY_PATH", new_callable=lambda: Path(tempfile.mkdtemp()) / "mem.json")
    def test_multiple_memories(self, _):
        mem.add_memory("Memory 1")
        mem.add_memory("Memory 2")
        mem.add_memory("Memory 3")
        entries = mem.load_memories()
        assert len(entries) == 3

    @patch("fluxlite.memory.MEMORY_PATH", new_callable=lambda: Path(tempfile.mkdtemp()) / "mem.json")
    def test_memory_persistence(self, _):
        mem.add_memory("Persistent memory")
        entries = mem.load_memories()
        assert len(entries) == 1
        assert entries[0]["content"] == "Persistent memory"

    @patch("fluxlite.memory.MEMORY_PATH", new_callable=lambda: Path(tempfile.mkdtemp()) / "mem.json")
    def test_load_corrupted_file(self, _):
        path = mem.MEMORY_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("not valid json", encoding="utf-8")
        entries = mem.load_memories()
        assert entries == []

    @patch("fluxlite.memory.MEMORY_PATH", new_callable=lambda: Path(tempfile.mkdtemp()) / "mem.json")
    def test_save_empty(self, _):
        mem.save_memories([])
        entries = mem.load_memories()
        assert entries == []
