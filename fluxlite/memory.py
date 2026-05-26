"""Dynamic memories — knowledge learned during conversation (~/.fluxlite/memory.json)."""
import json
from pathlib import Path
from datetime import datetime
from .i18n import _

MEMORY_PATH = Path.home() / ".fluxlite" / "memory.json"


def load_memories() -> list:
    if MEMORY_PATH.exists():
        try:
            data = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data.get("memories", [])
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, IOError, OSError):
            pass
    return []


def save_memories(entries: list):
    try:
        MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        MEMORY_PATH.write_text(
            json.dumps({"memories": entries}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except (OSError, PermissionError, TypeError):
        pass


def summarize_conversation(messages: list, provider, lang: str = "zh") -> str | None:
    """Summarize conversation using LLM and save as memory."""
    non_system = [m for m in messages if m["role"] != "system"]
    if len(non_system) < 4:
        return None

    content = "\n".join(
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m.get('content', '')[:300]}"
        for m in non_system[-20:]
    )

    prompt = _("memory_summary_prompt_en", content=content) if lang != "zh" else _("memory_summary_prompt_zh", content=content)

    try:
        result = provider.chat([{"role": "user", "content": prompt}], tools=[])
        summary = getattr(result, 'content', '') or ''
        summary = summary.strip()
        if summary:
            label = _("memory_summary_label")
            add_memory(f"[{label}] {summary}")
            return summary
    except Exception:
        pass
    return None


def add_memory(content: str) -> dict:
    entry = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "content": content,
        "created_at": datetime.now().isoformat(),
    }
    entries = load_memories()
    entries.append(entry)
    save_memories(entries)
    return entry
