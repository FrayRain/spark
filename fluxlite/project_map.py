"""Project map — rich snapshot of project structure with symbols and metadata."""
import re
import os
from pathlib import Path
from .i18n import _

SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".tox", ".egg-info", "dist", "build", ".idea", ".vscode",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".DS_Store",
    ".svn", "target", "bin", "obj", "site-packages", ".claude",
}
MAX_FILES = 150
MAX_DEPTH = 5


def _extract_symbols(path: Path) -> list[str]:
    """Extract class/function/interface definitions — only for small files."""
    size = path.stat().st_size
    if size > 10 * 1024:  # skip files larger than 10KB
        return []
    ext = path.suffix.lower()
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    symbols = []
    if ext == ".py":
        for m in re.finditer(r'^(?:class |async )?def |class |@(?:route|app\.|router\.)', text, re.MULTILINE):
            line = text[:m.start()].count("\n") + 1
            symbol = m.group().strip().rstrip(":")
            symbols.append(f"L{line}:{symbol}")
    elif ext in (".js", ".ts", ".jsx", ".tsx"):
        for m in re.finditer(r'^(?:export\s+)?(?:function\s+\w+|class\s+\w+|const\s+\w+\s*=\s*(?:async\s+)?\(|interface\s+\w+)', text, re.MULTILINE):
            line = text[:m.start()].count("\n") + 1
            symbols.append(f"L{line}:{m.group().strip()}")
    elif ext == ".rs":
        for m in re.finditer(r'^(?:fn\s+\w+|pub\s+(?:fn|struct|enum|trait|mod|type)\s+\w+)', text, re.MULTILINE):
            line = text[:m.start()].count("\n") + 1
            symbols.append(f"L{line}:{m.group().strip()}")
    elif ext == ".go":
        for m in re.finditer(r'^(?:func\s+\w+|type\s+\w+\s+(?:struct|interface))', text, re.MULTILINE):
            line = text[:m.start()].count("\n") + 1
            symbols.append(f"L{line}:{m.group().strip()}")
    elif ext == ".java":
        for m in re.finditer(r'^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:class|interface|enum|record)\s+\w+', text, re.MULTILINE):
            line = text[:m.start()].count("\n") + 1
            symbols.append(f"L{line}:{m.group().strip()}")
    elif ext in (".c", ".h", ".cpp", ".hpp", ".cc"):
        for m in re.finditer(r'^\s*(?:static\s+)?\w+\s+\w+\s*\(', text, re.MULTILINE):
            line = text[:m.start()].count("\n") + 1
            symbols.append(f"L{line}:fn {m.group().strip()}")
    return symbols[:20]


def _format_size(size: int) -> str:
    for unit in ["B", "KB", "MB"]:
        if size < 1024:
            return f"{size:.0f}{unit}"
        size //= 1024
    return f"{size:.0f}MB"


def build_project_map() -> str:
    """Build a compact project map with file sizes, symbols, and structure."""
    root = Path.cwd()
    lines = []
    lines.append(f"# {root.name}")
    lines.append("")

    # Count files by type
    ext_count: dict[str, int] = {}
    file_entries: list[tuple[Path, int, int]] = []
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            depth = Path(dirpath).relative_to(root).parts
            if len(depth) >= MAX_DEPTH:
                dirnames.clear()
                continue
            for fn in filenames:
                if fn.startswith("."):
                    continue
                fp = Path(dirpath) / fn
                try:
                    st = fp.stat()
                except OSError:
                    continue
                ext = fp.suffix.lower() or "(no ext)"
                ext_count[ext] = ext_count.get(ext, 0) + 1
                rel = fp.relative_to(root)
                file_entries.append((rel, st.st_size, len(rel.parts)))
    except OSError:
        return ""

    # File type summary
    sorted_exts = sorted(ext_count.items(), key=lambda x: -x[1])
    summary = ", ".join(f"{ext}×{n}" for ext, n in sorted_exts[:8])
    leftover = sum(n for _, n in sorted_exts[8:])
    if leftover:
        summary += f", others×{leftover}"
    lines.append(f"Files: {len(file_entries)}  ({summary})")
    lines.append("")

    # Build nested dict: directory names map to {"_files": [...]}
    # e.g. {"src": {"_files": [("main.py", 123, ...)], "utils": {"_files": [...]}}}
    root_node: dict = {"_files": []}
    for rel, size, _ in file_entries:
        parts = rel.parts
        node = root_node
        for p in parts[:-1]:
            node = node.setdefault(p, {"_files": []})
        node["_files"].append((parts[-1], size, rel))

    # Walk the tree and render lines
    file_count = 0

    def _walk(node, prefix="", is_last=True):
        nonlocal file_count
        dirs = [(k, v) for k, v in node.items() if k != "_files"]
        files = sorted(node.get("_files", []))
        total_items = len(dirs) + len(files)

        for idx, (name, subnode) in enumerate(dirs):
            if file_count >= MAX_FILES:
                return
            connector = "└── " if is_last and idx == total_items - 1 else "├── "
            lines.append(f"{prefix}{connector}{name}/")
            ext = "    " if is_last and idx == total_items - 1 else "│   "
            _walk(subnode, prefix + ext, idx == total_items - 1)

        for fi, (fname, fsize, frel) in enumerate(files):
            if file_count >= MAX_FILES:
                return
            idx = len(dirs) + fi
            connector = "└── " if is_last and idx == total_items - 1 else "├── "
            size_str = _format_size(fsize) if fsize > 0 else ""
            symbols = _extract_symbols(root / frel)
            sym_str = f"  [{', '.join(symbols[:5])}]" if symbols else ""
            lines.append(f"{prefix}{connector}{fname}  ({size_str}){sym_str}")
            file_count += 1

    _walk(root_node)
    if file_count >= MAX_FILES:
        lines.append(f"  ... ({len(file_entries) - MAX_FILES} more files)")

    return "\n".join(lines)
