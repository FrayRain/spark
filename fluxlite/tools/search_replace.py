"""Enhanced search and replace — fuzzy matching, context-aware, dry-run, and multi-file support."""
import re
import difflib
import json
import os
from pathlib import Path

SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".tox", ".egg-info", "dist", "build", ".idea", ".vscode",
    ".mypy_cache", ".pytest_cache", ".rufff_cache", ".DS_Store",
    ".svn", "target", "bin", "obj", "site-packages",
}

FUZZY_THRESHOLD = 0.75  # similarity ratio for fuzzy matching


def _is_text(fp: Path) -> bool:
    """Quick check if file is likely text."""
    try:
        with open(fp, "rb") as f:
            chunk = f.read(8192)
        return not bool(chunk) or b"\x00" not in chunk
    except OSError:
        return False


def _should_skip(fp: Path, root: Path) -> bool:
    """Check if file should be skipped (hidden or in ignored dir)."""
    try:
        rel = fp.relative_to(root)
        for p in rel.parents:
            if p.name.startswith(".") or p.name in SKIP_DIRS:
                return True
        return rel.name.startswith(".")
    except ValueError:
        return True


def _find_fuzzy_matches(content: str, pattern: str, threshold: float = FUZZY_THRESHOLD) -> list[tuple[str, float, int]]:
    """Find fuzzy matches of pattern in content lines.

    Returns list of (matched_line, similarity, line_number).
    """
    lines = content.splitlines()
    matches = []
    for i, line in enumerate(lines):
        ratio = difflib.SequenceMatcher(None, line.strip(), pattern.strip()).ratio()
        if ratio >= threshold:
            matches.append((line, ratio, i + 1))
    matches.sort(key=lambda x: -x[1])
    return matches


def _fuzzy_replace(content: str, old: str, new: str, threshold: float = FUZZY_THRESHOLD) -> tuple[str, int, list[dict]]:
    """Replace text using fuzzy matching. Returns (new_content, count, details)."""
    if old in content:
        # Exact match — fast path
        count = content.count(old)
        new_content = content.replace(old, new)
        return new_content, count, [{"type": "exact", "count": count}]

    # Try line-by-line fuzzy matching
    lines = content.splitlines(keepends=True)
    replacements = 0
    details = []
    new_lines = []

    for line in lines:
        stripped = line.rstrip("\n\r")
        ratio = difflib.SequenceMatcher(None, stripped, old).ratio()
        if ratio >= threshold:
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(indent + new + line[len(stripped):])
            replacements += 1
            details.append({"type": "fuzzy", "similarity": round(ratio, 3), "old": stripped})
        else:
            new_lines.append(line)

    if replacements > 0:
        return "".join(new_lines), replacements, details

    # Try substring fuzzy match within lines
    new_lines = []
    for line in lines:
        stripped = line.rstrip("\n\r")
        idx = stripped.find(old)
        if idx >= 0:
            new_line = stripped[:idx] + new + stripped[idx + len(old):]
            new_lines.append(new_line + line[len(stripped):])
            replacements += 1
            details.append({"type": "substring", "old": stripped})
        else:
            new_lines.append(line)

    if replacements > 0:
        return "".join(new_lines), replacements, details

    return content, 0, []


def search_replace_handler(
    pattern: str,
    replacement: str,
    glob: str = "**/*",
    path: str = ".",
    dry_run: bool = False,
    regex: bool = False,
    fuzzy: bool = False,
    context_lines: int = 0,
) -> str:
    """Search for a pattern in files and replace with new text.

    Supports exact, regex, and fuzzy matching modes. Use dry_run=True to
    preview changes. context_lines adds surrounding context in dry-run output.
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
    errors = []

    for fp in matches:
        if not fp.is_file() or _should_skip(fp, root) or not _is_text(fp):
            continue

        try:
            content = fp.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        rel = str(fp.relative_to(root))

        if regex:
            try:
                compiled = re.compile(pattern)
                count = len(compiled.findall(content))
                if count == 0:
                    continue
                if not dry_run:
                    new_content = compiled.sub(replacement, content)
                    fp.write_text(new_content, encoding="utf-8")
            except re.error as e:
                errors.append(f"  ! {rel}  regex error: {e}")
                continue

        elif fuzzy:
            new_content, count, details = _fuzzy_replace(content, pattern, replacement)
            if count == 0:
                continue
            if not dry_run:
                try:
                    fp.write_text(new_content, encoding="utf-8")
                except OSError as e:
                    errors.append(f"  ! {rel}  write failed: {e}")
                    continue

        else:
            # Exact match
            if pattern not in content:
                continue
            count = content.count(pattern)
            if not dry_run:
                new_content = content.replace(pattern, replacement)
                try:
                    fp.write_text(new_content, encoding="utf-8")
                except OSError as e:
                    errors.append(f"  ! {rel}  write failed: {e}")
                    continue

        if dry_run and context_lines > 0:
            # Show context around the match
            lines = content.splitlines()
            match_lines = set()
            if regex:
                for m in compiled.finditer(content):
                    line_no = content[:m.start()].count("\n")
                    for cl in range(max(0, line_no - context_lines), min(len(lines), line_no + context_lines + 1)):
                        match_lines.add(cl)
            elif pattern in content:
                idx = content.index(pattern)
                line_no = content[:idx].count("\n")
                for cl in range(max(0, line_no - context_lines), min(len(lines), line_no + context_lines + 1)):
                    match_lines.add(cl)

            preview_lines = []
            for ml in sorted(match_lines):
                marker = ">" if (pattern in lines[ml]) else " "
                preview_lines.append(f"    {marker} {ml + 1}:{lines[ml][:120]}")
            affected.append(f"  ~ {rel}  ({count} occurrences)\n" + "\n".join(preview_lines))
        else:
            affected.append(f"  ~ {rel}  ({count} occurrences)")

        total_replacements += count

    output = []
    if not affected and not errors:
        return f"[search_replace] No matches found for {pattern!r}"

    mode = "[REGEX] " if regex else "[FUZZY] " if fuzzy else ""
    header = f"[search_replace] {mode}{'[DRY RUN] ' if dry_run else ''}{pattern!r} → {replacement!r}: {len(affected)} files ({total_replacements} occurrences)"
    output.append(header)
    if affected:
        mode_note = " (with context)" if (dry_run and context_lines > 0) else ""
        output.append(f"  matches{mode_note}:")
        output.extend(affected)
    if errors:
        output.append("  errors:")
        output.extend(errors)
    return "\n".join(output)
