import os
from pathlib import Path

from ..i18n import _
from .sandbox import resolve_path as _sandbox_resolve
WINDOWS_BLOCKED = [
    Path("C:\\Windows"),
    Path("C:\\Program Files"),
    Path("C:\\Program Files (x86)"),
    Path("C:\\System32"),
    Path("C:\\Users\\All Users"),
]
UNIX_BLOCKED = [
    Path("/etc"),
    Path("/sys"),
    Path("/proc"),
    Path("/dev"),
    Path("/boot"),
    Path("/root"),
]


def _is_safe(path: Path) -> tuple[bool, str]:
    resolved = path.resolve()
    if os.name == "nt":
        for blocked in WINDOWS_BLOCKED:
            try:
                resolved.relative_to(blocked)
                return False, _("file_access_denied", path=blocked)
            except ValueError:
                continue
    else:
        for blocked in UNIX_BLOCKED:
            try:
                resolved.relative_to(blocked)
                return False, _("file_access_denied", path=blocked)
            except ValueError:
                continue
    return True, ""

def _safe_path(path_str: str) -> tuple[Path, str]:
    p = Path(path_str).resolve()
    safe, msg = _is_safe(p)
    if not safe:
        raise PermissionError(msg)
    return p, msg


def write(path: str, content: str) -> str:
    p, _ = _safe_path(_sandbox_resolve(path))
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    except OSError as e:
        return _("file_write_failed", e=e)
    return _("file_write_ok", len=len(content), path=p)


def read(path: str) -> str:
    sandboxed = _sandbox_resolve(path)
    p, _ = _safe_path(sandboxed)
    try:
        if p.exists():
            return p.read_text(encoding="utf-8")
    except (OSError, PermissionError) as e:
        return _("file_read_failed", e=e)
    p, _ = _safe_path(path)
    try:
        if not p.exists():
            return _("file_not_found", path=p)
        return p.read_text(encoding="utf-8")
    except (OSError, PermissionError) as e:
        return _("file_read_failed", e=e)


def edit(path: str, old_string: str, new_string: str) -> str:
    p, _ = _safe_path(_sandbox_resolve(path))
    if not p.exists():
        return _("file_not_found", path=p)
    try:
        content = p.read_text(encoding="utf-8")
    except (OSError, PermissionError) as e:
        return _("file_read_failed", e=e)
    if old_string not in content:
        return _("file_edit_not_found", path=p)
    new_content = content.replace(old_string, new_string, 1)
    try:
        p.write_text(new_content, encoding="utf-8")
    except (OSError, PermissionError) as e:
        return f"[file] Write failed: {e}"
    return _("file_edit_ok", path=p)


def append(path: str, content: str) -> str:
    p, _ = _safe_path(_sandbox_resolve(path))
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        return _("file_append_failed", e=e)
    return _("file_append_ok", len=len(content), path=p)


def delete(path: str) -> str:
    p, _ = _safe_path(_sandbox_resolve(path))
    if not p.exists():
        return _("file_not_found", path=p)
    try:
        p.unlink()
    except OSError as e:
        return _("file_delete_failed", e=e)
    return _("file_delete_ok", path=p)


def list_dir(path: str = ".", pattern: str = "") -> str:
    p, _ = _safe_path(_sandbox_resolve(path))
    if not p.exists():
        return f"[file] Directory not found: {p}"
    if not p.is_dir():
        return f"[file] Not a directory: {p}"

    if pattern:
        items = sorted(p.glob(pattern))
    else:
        items = sorted(p.iterdir())

    if not items:
        return f"[file] No files matching '{pattern}' in {p}"

    result = []
    for item in items:
        try:
            suffix = "/" if item.is_dir() else ""
            size = item.stat().st_size if item.is_file() else 0
        except OSError:
            result.append(f"  {item.name} (?)")
            continue
        if size:
            size_str = _format_size(size)
            result.append(f"  {item.name}{suffix} ({size_str})")
        else:
            result.append(f"  {item.name}{suffix}")
    return "\n".join(result)


def _format_size(size: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"
