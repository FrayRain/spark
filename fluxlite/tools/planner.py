"""Task planner + self-review tools for structured AI workflows.

Forces the AI to explicitly plan before executing and review after
completing, reducing rework on complex tasks.
"""

import uuid
import json
from datetime import datetime

from ..i18n import _

_plans: dict[str, dict] = {}
_ACTIVE_PLAN_ID: str | None = None


def _progress_bar_str(done: int, total: int, width: int = 15) -> str:
    """Build a visual progress bar string: ████░░░ 3/5"""
    if total <= 0:
        return ""
    filled = int(done / total * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"{bar}  {done}/{total}"


def set_active_plan(pid: str):
    global _ACTIVE_PLAN_ID
    _ACTIVE_PLAN_ID = pid


def clear_active_plan():
    global _ACTIVE_PLAN_ID
    _ACTIVE_PLAN_ID = None


def plan_progress() -> tuple[str, int, int]:
    """Return (goal, done, total) for the active plan, or ('', 0, 0)."""
    global _ACTIVE_PLAN_ID
    if not _ACTIVE_PLAN_ID or _ACTIVE_PLAN_ID not in _plans:
        return "", 0, 0
    plan = _plans[_ACTIVE_PLAN_ID]
    total = len(plan["steps"])
    done = sum(1 for s in plan["steps"] if s["status"] == "done")
    return plan["goal"], done, total


def task_planner_handler(goal: str = "", steps: str = "", context: str = "") -> str:
    if not goal:
        return _("plan_no_goal")

    if not steps:
        return _("plan_no_steps")

    pid = f"plan_{datetime.now().strftime('%H%M%S')}_{uuid.uuid4().hex[:4]}"

    step_list = []
    for line in steps.split("\n"):
        line = line.strip()
        if not line:
            continue
        clean = line.lstrip("0123456789. )-* \t")
        if clean:
            step_list.append(clean)

    plan = {
        "id": pid,
        "goal": goal,
        "context": context,
        "steps": [{"desc": s, "status": "pending"} for s in step_list],
        "created_at": datetime.now().isoformat(),
    }
    _plans[pid] = plan
    set_active_plan(pid)

    total = len(plan["steps"])
    bar = _progress_bar_str(0, total)
    lines = [
        _("plan_header", id=pid),
        _("plan_goal", goal=goal),
        "",
        _("plan_progress", bar=bar),
        _("plan_steps"),
    ]
    for i, s in enumerate(plan["steps"]):
        lines.append(f"  [{i+1}] . {s['desc']}")
    lines.append("")
    lines.append(_("plan_footer"))
    return "\n".join(lines)


def self_review_handler(
    plan_id: str = "",
    result_summary: str = "",
    completed_steps: str = "",
) -> str:
    if not plan_id:
        return _("plan_no_id")

    lines = [
        _("plan_review_header"),
        f"Plan: {plan_id}",
        "",
    ]

    if plan_id in _plans:
        plan = _plans[plan_id]
        lines.append(_("plan_goal", goal=plan['goal']))
        lines.append("")

        done_set = set()
        for part in completed_steps.split(","):
            part = part.strip()
            if part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < len(plan["steps"]):
                    plan["steps"][idx]["status"] = "done"
                    done_set.add(idx)

        done_set_len = len(done_set)
        bar = _progress_bar_str(done_set_len, len(plan["steps"]))
        lines.append(_("plan_progress", bar=bar))
        for i, s in enumerate(plan["steps"]):
            if s["status"] == "done":
                lines.append(f"  [x] Step {i+1}: {s['desc']}")
            else:
                lines.append(f"  [ ] Step {i+1}: {s['desc']}")
        lines.append("")

        if done_set_len == len(plan["steps"]):
            clear_active_plan()
    else:
        lines.append(_("plan_not_found", id=plan_id))
        lines.append("")

    if result_summary:
        lines.append(_("plan_review_result"))
        lines.append(f"  {result_summary}")
        lines.append("")

    lines.append("Checklist:")
    lines.append(_("plan_checklist_1"))
    lines.append(_("plan_checklist_2"))
    lines.append(_("plan_checklist_3"))
    lines.append(_("plan_checklist_4"))
    lines.append(_("plan_checklist_5"))
    lines.append("")
    lines.append(_("plan_review_footer"))

    return "\n".join(lines)
