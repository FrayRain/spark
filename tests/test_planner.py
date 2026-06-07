"""Tests for tools/planner.py — progress bar, plan lifecycle, self-review."""
import pytest
from fluxlite.tools.planner import (
    _progress_bar_str, task_planner_handler, self_review_handler,
    plan_progress, set_active_plan, clear_active_plan,
    _plans,
)


def _clear_plans():
    _plans.clear()
    clear_active_plan()


# ---------------------------------------------------------------------------
# _progress_bar_str
# ---------------------------------------------------------------------------

class TestProgressBar:
    def test_empty_total(self):
        assert _progress_bar_str(0, 0) == ""

    def test_full(self):
        result = _progress_bar_str(5, 5)
        assert "5/5" in result
        assert "█" in result

    def test_partial(self):
        result = _progress_bar_str(2, 5)
        assert "2/5" in result
        assert "░" in result

    def test_zero_done(self):
        result = _progress_bar_str(0, 5, width=10)
        assert "0/5" in result
        assert "░" * 10 in result

    def test_custom_width(self):
        result = _progress_bar_str(3, 6, width=6)
        assert "3/6" in result
        # 3/6 = 50% → 3 filled, 3 empty
        assert len(result.split()[0]) == 6


# ---------------------------------------------------------------------------
# task_planner_handler
# ---------------------------------------------------------------------------

class TestTaskPlanner:
    def setup_method(self):
        _clear_plans()

    def test_missing_goal(self):
        result = task_planner_handler(goal="", steps="do it")
        assert len(result) > 0
        # Should not look like a successful plan
        assert "[1]" not in result or "goal" in result

    def test_missing_steps(self):
        result = task_planner_handler(goal="fix bug", steps="")
        assert len(result) > 0
        # Should not look like a successful plan
        assert "progress" not in result.lower()

    def test_creates_plan(self):
        result = task_planner_handler(goal="refactor", steps="step1\nstep2\nstep3")
        assert "refactor" in result.lower() or "plan" in result.lower()
        assert len(_plans) > 0

    def test_steps_parsed(self):
        result = task_planner_handler(goal="test", steps="1. first\n2. second\n- third")
        lines = result.split("\n")
        step_lines = [l for l in lines if "[1]" in l or "[2]" in l or "[3]" in l]
        assert len(step_lines) >= 1

    def test_sets_active_plan(self):
        task_planner_handler(goal="g", steps="s1\ns2")
        goal, done, total = plan_progress()
        assert done == 0
        assert total >= 2


# ---------------------------------------------------------------------------
# plan_progress / set_active / clear_active
# ---------------------------------------------------------------------------

class TestPlanProgress:
    def setup_method(self):
        _clear_plans()

    def test_no_active_plan(self):
        goal, done, total = plan_progress()
        assert goal == ""
        assert done == 0
        assert total == 0

    def test_after_clear(self):
        task_planner_handler(goal="g", steps="s1")
        clear_active_plan()
        goal, done, total = plan_progress()
        assert goal == ""

    def test_tracks_progress_after_review(self):
        task_planner_handler(goal="g", steps="s1\ns2\ns3")
        self_review_handler(plan_id=list(_plans.keys())[0], completed_steps="1,2")
        goal, done, total = plan_progress()
        assert done == 2
        assert total == 3


# ---------------------------------------------------------------------------
# self_review_handler
# ---------------------------------------------------------------------------

class TestSelfReview:
    def setup_method(self):
        _clear_plans()

    def test_missing_plan_id(self):
        result = self_review_handler(plan_id="")
        assert "id" in result.lower() or "plan_no_id" in result

    def test_plan_not_found(self):
        result = self_review_handler(plan_id="nonexistent")
        assert "nonexistent" in result

    def test_marks_steps_done(self):
        task_planner_handler(goal="g", steps="s1\ns2")
        pid = list(_plans.keys())[0]
        result = self_review_handler(plan_id=pid, completed_steps="1")
        assert "[x]" in result
        assert "[ ]" in result

    def test_clears_plan_when_all_done(self):
        task_planner_handler(goal="g", steps="s1")
        pid = list(_plans.keys())[0]
        self_review_handler(plan_id=pid, completed_steps="1")
        goal, done, total = plan_progress()
        assert goal == "" or done == total  # cleared or all done
