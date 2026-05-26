"""Smart refactoring — AST-aware symbol rename with safety checks."""
import ast
import re
import tokenize
import io
from pathlib import Path
from ..i18n import _

SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".tox", ".egg-info", "dist", "build", ".idea", ".vscode",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".DS_Store",
    ".svn", "target", "bin", "obj", "site-packages",
}


def _should_skip(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
        return any(
            p.name.startswith(".") or p.name in SKIP_DIRS
            for p in rel.parents
        ) or rel.name.startswith(".")
    except ValueError:
        return True


def _is_python_file(path: Path) -> bool:
    return path.suffix == ".py"


def _python_rename_in_file(
    path: Path, old_name: str, new_name: str, dry_run: bool
) -> tuple[bool, str]:
    """Rename a symbol in a Python file using tokenize to skip strings/comments."""
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False, ""

    # Fast check
    if old_name not in source:
        return False, ""

    # Use tokenize to find NAME tokens matching old_name (skips strings/comments)
    replacements = []
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except tokenize.TokenError:
        return False, ""

    for tok in tokens:
        if tok.type == tokenize.NAME and tok.string == old_name:
            start = tok.start
            end_row, end_col = tok.end
            # Compute flat index from line/col
            lines = source.split("\n")
            line_start = sum(len(lines[i]) + 1 for i in range(start[0] - 1)) + start[1]
            line_end = sum(len(lines[i]) + 1 for i in range(end_row - 1)) + end_col
            replacements.append((line_start, line_end))

    if not replacements:
        return False, ""

    count = len(replacements)
    if not dry_run:
        # Apply in reverse order to preserve positions
        result = source
        for start, end in sorted(replacements, reverse=True):
            result = result[:start] + new_name + result[end:]
        path.write_text(result, encoding="utf-8")

    return True, f"{path.name}: {count} occurrence{'s' if count > 1 else ''}"


def _generic_rename_in_file(
    path: Path, old_name: str, new_name: str, dry_run: bool
) -> tuple[bool, str]:
    """Word-boundary rename for non-Python files."""
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False, ""

    if old_name not in source:
        return False, ""

    pattern = re.compile(rf'\b{re.escape(old_name)}\b')
    matches = list(pattern.finditer(source))
    if not matches:
        return False, ""

    count = len(matches)
    if not dry_run:
        result = pattern.sub(new_name, source)
        path.write_text(result, encoding="utf-8")

    return True, f"{path.name}: {count} occurrence{'s' if count > 1 else ''}"


def refactor_rename_handler(
    old_name: str,
    new_name: str,
    path: str = ".",
    glob: str = "**/*.py",
    dry_run: bool = False,
) -> str:
    """Rename a symbol across files with word-boundary matching.

    For Python files (.py), uses tokenize to skip strings and comments.
    For other files, uses regex word-boundary matching.
    Use dry_run=True to preview without making changes.
    """
    if not old_name or not new_name:
        return _("refactor_missing_params")

    root = Path(path).resolve()
    if not root.is_dir():
        return f"[refactor_rename] Not a directory: {path}"

    try:
        matches = list(root.rglob(glob))
    except (OSError, ValueError) as e:
        return f"[refactor_rename] Glob error: {e}"

    affected = []
    total_replacements = 0

    for fp in matches:
        if not fp.is_file() or _should_skip(fp, root):
            continue

        if _is_python_file(fp):
            ok, desc = _python_rename_in_file(fp, old_name, new_name, dry_run)
        else:
            ok, desc = _generic_rename_in_file(fp, old_name, new_name, dry_run)

        if ok:
            affected.append(f"  ~ {desc}  ({fp.relative_to(root)})")
            count = int(desc.split(":")[1].strip().split()[0]) if ":" in desc else 1
            total_replacements += count

    if not affected:
        return _("refactor_no_matches", name=old_name)

    header = (
        f"[refactor_rename] {'[DRY RUN] ' if dry_run else ''}"
        f"Renamed {old_name!r} → {new_name!r}"
        f" in {len(affected)} files ({total_replacements} occurrences)"
    )
    if dry_run:
        header += _("refactor_dry_run")
    return header + "\n" + "\n".join(affected)
