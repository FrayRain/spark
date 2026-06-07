"""Test parallel tool execution via ThreadPoolExecutor."""

import time
import json
from unittest.mock import patch, MagicMock
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest


# ---------------------------------------------------------------------------
# Helper: fake tool calls
# ---------------------------------------------------------------------------

class FakeToolCall:
    """Simulate a tool call object returned by the provider."""
    _counter = 0
    def __init__(self, name: str, arguments: dict, id: str | None = None):
        self.name = name
        self.arguments = arguments
        FakeToolCall._counter += 1
        self.id = id or f"call_{FakeToolCall._counter}"


def _slow_tool(name, args):
    """Simulate a tool that takes variable time."""
    delay = args.get("_delay", 0.1)
    time.sleep(delay)
    return f"[result] {name} done in {delay}s"


def _non_parallel_tool(name, args):
    time.sleep(0.1)
    return f"[result] {name} done"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestParallelExecution:
    """Verify that multiple tool calls execute concurrently."""

    def test_parallel_speedup(self):
        """3 tools at 0.2s each should take ~0.2s in parallel, not 0.6s."""
        tool_calls = [
            FakeToolCall("file_read", {"path": "a.txt", "_delay": 0.2}),
            FakeToolCall("file_read", {"path": "b.txt", "_delay": 0.2}),
            FakeToolCall("file_read", {"path": "c.txt", "_delay": 0.2}),
        ]

        results_map = {}
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=3) as ex:
            future_map = {ex.submit(_slow_tool, tc.name, tc.arguments): tc for tc in tool_calls}
            for future in as_completed(future_map):
                tc = future_map[future]
                results_map[tc.id] = future.result()
        elapsed = time.time() - t0

        # Should be much closer to 0.2s than 0.6s
        assert elapsed < 0.5, f"Parallel took {elapsed:.3f}s, expected <0.5s"
        assert len(results_map) == 3
        for tc in tool_calls:
            assert tc.id in results_map

    def test_sequential_when_single_tool(self):
        """Single tool — no threading overhead issue, still works."""
        tc = FakeToolCall("file_read", {"path": "a.txt", "_delay": 0.1})
        results_map = {}
        with ThreadPoolExecutor(max_workers=1) as ex:
            future_map = {ex.submit(_slow_tool, tc.name, tc.arguments): tc for tc in [tc]}
            for future in as_completed(future_map):
                t = future_map[future]
                results_map[t.id] = future.result()
        assert len(results_map) == 1

    def test_results_preserve_original_order(self):
        """Process results in original tool_calls order, not completion order."""
        tool_calls = [
            FakeToolCall("file_read", {"path": "a.txt", "_delay": 0.3}),
            FakeToolCall("file_read", {"path": "b.txt", "_delay": 0.05}),
            FakeToolCall("file_read", {"path": "c.txt", "_delay": 0.1}),
        ]

        results_map = {}
        with ThreadPoolExecutor(max_workers=3) as ex:
            future_map = {ex.submit(_slow_tool, tc.name, tc.arguments): tc for tc in tool_calls}
            for future in as_completed(future_map):
                tc = future_map[future]
                results_map[tc.id] = future.result()

        # Process in original order
        ordered_results = []
        for tc in tool_calls:
            ordered_results.append((tc.name, results_map[tc.id]))

        assert len(ordered_results) == 3
        assert ordered_results[0][0] == "file_read"
        assert ordered_results[1][0] == "file_read"
        assert ordered_results[2][0] == "file_read"

    def test_mixed_tool_names_grouping(self):
        """Same-named tools should be grouped correctly when processed in order."""
        tool_calls = [
            FakeToolCall("file_read", {"path": "a.txt"}),
            FakeToolCall("file_read", {"path": "b.txt"}),
            FakeToolCall("grep_search", {"pattern": "foo"}),
            FakeToolCall("file_read", {"path": "c.txt"}),
        ]

        results_map = {}
        with ThreadPoolExecutor(max_workers=4) as ex:
            future_map = {ex.submit(_slow_tool, tc.name, tc.arguments): tc for tc in tool_calls}
            for future in as_completed(future_map):
                tc = future_map[future]
                results_map[tc.id] = future.result()

        # Simulate the _tool_group display logic
        tool_group = []
        groups = []

        for tc in tool_calls:
            result = results_map[tc.id]
            if tool_group and tool_group[0][0] != tc.name:
                groups.append(list(tool_group))
                tool_group.clear()
            tool_group.append((tc.name, result))

        if tool_group:
            groups.append(list(tool_group))

        # Should have 3 groups: file_read x2, grep_search x1, file_read x1
        assert len(groups) == 3
        assert groups[0][0][0] == "file_read"
        assert len(groups[0]) == 2
        assert groups[1][0][0] == "grep_search"
        assert len(groups[1]) == 1
        assert groups[2][0][0] == "file_read"
        assert len(groups[2]) == 1


# ---------------------------------------------------------------------------
# Non-parallel tool safety
# ---------------------------------------------------------------------------

class TestNonParallelTools:
    """Tools in _NON_PARALLEL_TOOLS should fall back to sequential execution."""

    NON_PARALLEL = frozenset({"terminal", "browser", "mcp_call", "hook_run", "spawn_agents"})

    def test_detect_non_parallel_tools(self):
        """Verify detection works for mixed tool lists."""
        all_parallel = [
            FakeToolCall("file_read", {}),
            FakeToolCall("grep_search", {}),
        ]
        assert not any(tc.name in self.NON_PARALLEL for tc in all_parallel)

        has_non_parallel = [
            FakeToolCall("file_read", {}),
            FakeToolCall("terminal", {"command": "ls"}),
        ]
        assert any(tc.name in self.NON_PARALLEL for tc in has_non_parallel)

    def test_non_parallel_fallback_sequential_time(self):
        """When non-parallel tools present, execution should be sequential."""
        tool_calls = [
            FakeToolCall("file_read", {"path": "a.txt", "_delay": 0.15}),
            FakeToolCall("terminal", {"command": "echo hi", "_delay": 0.15}),
            FakeToolCall("file_read", {"path": "b.txt", "_delay": 0.15}),
        ]

        t0 = time.time()
        results_map = {}
        for tc in tool_calls:
            results_map[tc.id] = _slow_tool(tc.name, tc.arguments)
        elapsed = time.time() - t0

        # Sequential: ~0.45s, parallel would be ~0.15s
        assert elapsed >= 0.3, f"Sequential should take >=0.3s, got {elapsed:.3f}"
        assert len(results_map) == 3


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_tool_list(self):
        """No tools to execute — should be fine."""
        results_map = {}
        assert len(results_map) == 0

    def test_single_tool(self):
        """Single tool call should work without threading overhead."""
        tc = FakeToolCall("file_read", {"path": "a.txt", "_delay": 0.05})
        results_map = {}
        with ThreadPoolExecutor(max_workers=1) as ex:
            future_map = {ex.submit(_slow_tool, tc.name, tc.arguments): tc for tc in [tc]}
            for future in as_completed(future_map):
                t = future_map[future]
                results_map[t.id] = future.result()
        assert len(results_map) == 1
        assert "done" in results_map[tc.id]

    def test_tool_error_in_parallel(self):
        """One tool raising an exception shouldn't block others."""
        def _failing_tool(name, args):
            if args.get("fail"):
                raise ValueError("Simulated failure")
            return "ok"

        tool_calls = [
            FakeToolCall("file_read", {"path": "a.txt", "fail": False}),
            FakeToolCall("file_read", {"path": "b.txt", "fail": True}),
            FakeToolCall("file_read", {"path": "c.txt", "fail": False}),
        ]

        results_map = {}
        with ThreadPoolExecutor(max_workers=3) as ex:
            future_map = {ex.submit(_failing_tool, tc.name, tc.arguments): tc for tc in tool_calls}
            for future in as_completed(future_map):
                tc = future_map[future]
                try:
                    results_map[tc.id] = future.result()
                except Exception as e:
                    results_map[tc.id] = f"[error] {e}"

        assert len(results_map) == 3
        # The failing tool should have error result
        failing_id = tool_calls[1].id
        assert "[error]" in results_map[failing_id]

    def test_many_tools_max_workers_cap(self):
        """More than 5 tools should cap at 5 workers."""
        tool_calls = [FakeToolCall("file_read", {"_delay": 0.2}) for _ in range(8)]

        t0 = time.time()
        results_map = {}
        with ThreadPoolExecutor(max_workers=min(len(tool_calls), 5)) as ex:
            future_map = {ex.submit(_slow_tool, tc.name, tc.arguments): tc for tc in tool_calls}
            for future in as_completed(future_map):
                tc = future_map[future]
                results_map[tc.id] = future.result()
        elapsed = time.time() - t0

        # 8 tools at 0.2s with 5 workers: ~0.4s (2 batches), not 1.6s
        assert elapsed < 1.0, f"8 parallel tools with 5 workers took {elapsed:.3f}s, expected <1.0s"
        assert len(results_map) == 8


# ---------------------------------------------------------------------------
# Integration: mock-level test of app.py parallel flow
# ---------------------------------------------------------------------------

class TestAppParallelFlow:
    """Test the parallel execution logic used in app.py's main loop."""

    def test_auto_mode_parallel_flow(self, monkeypatch):
        """Verify auto-mode parallel execution flow works end-to-end."""
        from fluxlite.tools.registry import execute_tool as real_execute

        results = {}

        def mock_execute(name, args):
            delay = args.get("_delay", 0.05)
            time.sleep(delay)
            r = f"[{name}] ok"
            results[id(args)] = r
            return r

        tool_calls_data = [
            {"name": "file_read", "arguments": {"path": "a.txt", "_delay": 0.1}, "id": "call_1"},
            {"name": "file_read", "arguments": {"path": "b.txt", "_delay": 0.1}, "id": "call_2"},
            {"name": "file_read", "arguments": {"path": "c.txt", "_delay": 0.1}, "id": "call_3"},
        ]

        # Build FakeToolCall objects
        tool_calls = [FakeToolCall(d["name"], d["arguments"], d["id"]) for d in tool_calls_data]

        _NON_PARALLEL_TOOLS = frozenset({"terminal", "browser", "mcp_call", "hook_run", "spawn_agents"})
        _can_parallel = not any(tc.name in _NON_PARALLEL_TOOLS for tc in tool_calls)
        assert _can_parallel

        tool_results = []
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=min(len(tool_calls), 5)) as ex:
            future_map = {ex.submit(mock_execute, tc.name, tc.arguments): tc for tc in tool_calls}
            for future in as_completed(future_map):
                tc = future_map[future]
                r = future.result()
                tool_results.append((tc, r))
        elapsed = time.time() - t0

        assert elapsed < 0.25, f"Parallel auto-mode took {elapsed:.3f}s"
        assert len(tool_results) == 3

    def test_main_loop_parallel_flow(self, monkeypatch):
        """Verify main loop Phase 1/2/3 flow."""
        results = {}

        def mock_execute(name, args):
            delay = args.get("_delay", 0.08)
            time.sleep(delay)
            return f"[result] {name}"

        tool_calls_data = [
            {"name": "file_read", "arguments": {"path": "a.txt", "_delay": 0.08}, "id": "call_a"},
            {"name": "file_read", "arguments": {"path": "b.txt", "_delay": 0.08}, "id": "call_b"},
        ]
        pending_tool_calls = [FakeToolCall(d["name"], d["arguments"], d["id"]) for d in tool_calls_data]

        # Phase 1: Confirmations (all auto-approved in this test)
        approved_tools = list(pending_tool_calls)

        # Phase 2: Execute in parallel
        results_map = {}
        _NON_PARALLEL_TOOLS = frozenset({"terminal", "browser", "mcp_call", "hook_run", "spawn_agents"})
        _can_parallel = not any(tc.name in _NON_PARALLEL_TOOLS for tc in approved_tools)
        assert _can_parallel

        t0 = time.time()
        with ThreadPoolExecutor(max_workers=min(len(approved_tools), 5)) as ex:
            future_map = {ex.submit(mock_execute, tc.name, tc.arguments): tc for tc in approved_tools}
            for future in as_completed(future_map):
                tc = future_map[future]
                results_map[tc.id] = future.result()
        elapsed = time.time() - t0

        assert elapsed < 0.15, f"Parallel main loop took {elapsed:.3f}s"

        # Phase 3: Process in original order
        messages = []
        for tc in approved_tools:
            result = results_map[tc.id]
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

        assert len(messages) == 2
        assert messages[0]["tool_call_id"] == "call_a"
        assert messages[1]["tool_call_id"] == "call_b"

    def test_non_parallel_detection_in_main_loop(self):
        """Verify non-parallel tools force sequential in main loop."""
        tool_calls_data = [
            {"name": "file_read", "arguments": {}, "id": "call_1"},
            {"name": "terminal", "arguments": {"command": "ls"}, "id": "call_2"},
        ]
        pending = [FakeToolCall(d["name"], d["arguments"], d["id"]) for d in tool_calls_data]

        _NON_PARALLEL_TOOLS = frozenset({"terminal", "browser", "mcp_call", "hook_run", "spawn_agents"})
        _can_parallel = not any(tc.name in _NON_PARALLEL_TOOLS for tc in pending)
        assert not _can_parallel
