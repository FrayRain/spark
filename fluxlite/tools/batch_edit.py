"""Batch edit — atomic multi-file edits with rollback."""
import json
import shutil
import tempfile
from pathlib import Path
from . import file_ops
from .sandbox import resolve_path as _sandbox_resolve
from ..i18n import _


def batch_edit_handler(edits: str) -> str:
    """Apply multiple file edits atomically.

    edits is a JSON array:
    [
      {"path": "src/main.py", "old_string": "foo", "new_string": "bar"},
      {"path": "src/utils.py", "old_string": "import os", "new_string": "from pathlib import Path"},
      {"path": "new_file.py", "content": "# new file"}
    ]

    All edits are applied, then verified. On any failure, ALL changes are rolled back.
    """
    try:
        edit_list = json.loads(edits)
    except json.JSONDecodeError as e:
        return _("batch_invalid_json", e=e)

    if not isinstance(edit_list, list) or not edit_list:
        return "[batch_edit] Expected a non-empty JSON array of edits"

    # Validate all edits first
    for i, edit in enumerate(edit_list):
        if not isinstance(edit, dict):
            return f"[batch_edit] Edit #{i+1} is not a JSON object"
        path = edit.get("path", "")
        if not path:
            return f"[batch_edit] Edit #{i+1} is missing 'path'"
        has_edit = "old_string" in edit and "new_string" in edit
        has_new = "content" in edit
        if not has_edit and not has_new:
            return f"[batch_edit] Edit #{i+1} needs 'old_string'+'new_string' or 'content'"
        if has_edit and has_new:
            return f"[batch_edit] Edit #{i+1} has both edit fields and 'content' — use one or the other"
        if has_edit:
            if not isinstance(edit.get("old_string"), str) or not isinstance(edit.get("new_string"), str):
                return f"[batch_edit] Edit #{i+1}: 'old_string' and 'new_string' must be strings"

    # Collect all original file contents for rollback
    backups: dict[str, tuple[Path, str | None]] = {}  # path -> (resolved_path, original_content or None)
    resolved_paths: dict[str, Path] = {}

    try:
        for edit in edit_list:
            raw_path = _sandbox_resolve(edit["path"])
            p = Path(raw_path).resolve()
            resolved_paths[edit["path"]] = p
            if p.exists():
                backups[edit["path"]] = (p, p.read_text(encoding="utf-8"))
            else:
                backups[edit["path"]] = (p, None)

        # Apply all edits
        results = []
        for edit in edit_list:
            p = resolved_paths[edit["path"]]
            has_new = "content" in edit
            if has_new:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(edit["content"], encoding="utf-8")
                results.append(f"  + {edit['path']}  ({len(edit['content'])} chars)")
            else:
                if not p.exists():
                    raise RuntimeError(f"File not found: {edit['path']}")
                content = p.read_text(encoding="utf-8")
                if edit["old_string"] not in content:
                    raise RuntimeError(
                        f"old_string not found in {edit['path']} "
                        f"(looked for {edit['old_string'][:50]!r})"
                    )
                new_content = content.replace(edit["old_string"], edit["new_string"], 1)
                p.write_text(new_content, encoding="utf-8")
                results.append(f"  ~ {edit['path']}  (1 replacement)")

        return _("batch_all_ok") + "\n" + "\n".join(results)

    except Exception as e:
        # Rollback all changes
        errors = []
        for orig_path, (p, orig_content) in backups.items():
            try:
                if orig_content is None:
                    if p.exists():
                        p.unlink()
                else:
                    p.write_text(orig_content, encoding="utf-8")
            except Exception as rollback_err:
                errors.append(f"    rollback failed for {orig_path}: {rollback_err}")

        msg = _("batch_failed", e=e)
        if errors:
            msg += _("batch_rollback_warning") + "\n" + "\n".join(errors)
        return msg
