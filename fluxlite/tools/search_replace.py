"""Search and replace — pattern-based global replacement with dry-run support."""
import re
import os
from pathlib import Path
from ..i18n import _

SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".tox", ".egg-info", "dist", "build", ".idea", ".vscode",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".DS_Store",
    ".svn", "target", "bin", "obj", "site-packages",
}


def search_replace_handler(pattern: str, replacement: str, glob: str = "**/*", path: str = ".", dry_run: bool = False) -> str:
    """Search for a pattern in files and replace with new text.

    Uses simple string replacement (not regex). Set dry_run=True to preview
    without making changes. Use glob to filter which files to scan.
    """
    root = Path(path).resolve()
    if not root.is_dir():
        return f"[search_replace] Not a directory: {path}"

    try:
        matches = list(root.rglob(glob))
    except (OSError, ValueError) as e:
        return f"[search_replace] Glob error: {e}"

    affected = []
    total_replacements = 0

    for fp in matches:
        if not fp.is_file():
            continue
        # Skip hidden files and ignored directories
        try:
            rel = fp.relative_to(root)
            if any(p.name.startswith(".") or p.name in SKIP_DIRS for p in rel.parents):
                continue
            if rel.name.startswith("."):
                continue
        except ValueError:
            continue

        try:
            content = fp.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        if pattern not in content:
            continue

        count = content.count(pattern)
        if not dry_run:
            new_content = content.replace(pattern, replacement)
            try:
                fp.write_text(new_content, encoding="utf-8")
            except OSError as e:
                affected.append(f"  ! {rel}  {_('srch_write_failed', e=e)}")
                continue

        affected.append(f"  ~ {rel}  ({count} occurrence{'s' if count > 1 else ''})")
        total_replacements += count

    if not affected:
        return _("srch_no_matches", pattern=pattern)

    header = f"[search_replace] {'[DRY RUN] ' if dry_run else ''}Found {pattern!r} in {len(affected)} files ({total_replacements} total occurrences):"
    if dry_run:
        header += _("srch_dry_run")
    return header + "\n" + "\n".join(affected)
