"""Project context builders — FLUXLITE.md, git state, directory tree, /init generator."""
import subprocess
from pathlib import Path
from datetime import datetime
from .i18n import _

# ── Constants ──

PROJECT_TREE_DEPTH = 3
PROJECT_TREE_SKIP = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".tox", ".egg-info", "dist", "build", ".idea", ".vscode",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".DS_Store",
    ".svn", "target", "bin", "obj", "site-packages",
}


# ── Context readers ──

def build_fluxlite_md() -> str:
    """Read FLUXLITE.md from cwd or .fluxlite/."""
    cwd = Path.cwd()
    for p in [cwd / "FLUXLITE.md", cwd / ".fluxlite" / "FLUXLITE.md"]:
        if p.exists():
            try:
                return p.read_text(encoding="utf-8").strip()
            except (OSError, PermissionError, UnicodeDecodeError):
                pass
    return ""


def build_project_memory() -> str:
    """Read .fluxlite/project_memory.md."""
    cwd = Path.cwd()
    p = cwd / ".fluxlite" / "project_memory.md"
    if p.exists():
        try:
            return p.read_text(encoding="utf-8").strip()
        except (OSError, PermissionError):
            pass
    return ""


def build_instructions_md() -> str:
    """Read INSTRUCTIONS.md or .fluxlite/instructions.md."""
    cwd = Path.cwd()
    for p in [cwd / "INSTRUCTIONS.md", cwd / ".fluxlite" / "instructions.md"]:
        if p.exists():
            try:
                return p.read_text(encoding="utf-8").strip()
            except (OSError, PermissionError):
                pass
    return ""


def build_project_tree(max_depth: int = PROJECT_TREE_DEPTH,
                       skip_set: set = None) -> str:
    """Generate a compact directory tree of the current project."""
    if skip_set is None:
        skip_set = PROJECT_TREE_SKIP
    root = Path.cwd()
    lines = []

    def _walk(dirpath: Path, prefix: str = "", depth: int = 0):
        if depth > max_depth:
            return
        try:
            entries = sorted(dirpath.iterdir(),
                           key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            return

        for i, entry in enumerate(entries):
            if entry.name in skip_set or entry.name.startswith("."):
                continue
            is_last = (i == len(entries) - 1)
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{entry.name}{'/' if entry.is_dir() else ''}")
            if entry.is_dir():
                ext = "    " if is_last else "│   "
                _walk(entry, prefix + ext, depth + 1)

    lines.append(root.name + "/")
    _walk(root)
    return "\n".join(lines) if len(lines) > 1 else ""


def build_git_context() -> str:
    """Collect git branch, status, and recent log in parallel."""
    import subprocess as _sp
    try:
        # Run independent git commands in parallel
        proc_branch = _sp.Popen(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stdout=_sp.PIPE, stderr=_sp.PIPE, text=True,
        )
        proc_status = _sp.Popen(
            ["git", "status", "--short"],
            stdout=_sp.PIPE, stderr=_sp.PIPE, text=True,
        )
        proc_log = _sp.Popen(
            ["git", "log", "--oneline", "-5"],
            stdout=_sp.PIPE, stderr=_sp.PIPE, text=True,
        )

        branch_out, _ = proc_branch.communicate(timeout=5)
        status_out, _ = proc_status.communicate(timeout=5)
        log_out, _ = proc_log.communicate(timeout=5)

        branch = branch_out.strip()
        if not branch or branch.startswith("fatal"):
            return ""

        parts = [f"Branch: {branch}"]

        status = status_out.strip()
        if status:
            parts.append(f"Status:\n{status}")

        log = log_out.strip()
        if log:
            parts.append(f"Recent:\n{log}")

        return "\n\n".join(parts)
    except (_sp.TimeoutExpired, OSError, PermissionError):
        return ""


# ── /init generator ──

def generate_fluxlite_md(console, radio_select) -> None:
    """Scan current project and generate FLUXLITE.md (interactive)."""
    cwd = Path.cwd()
    target = cwd / "FLUXLITE.md"

    if target.exists():
        choice = radio_select(_("proj_fluxlite_exists"), [
            ("overwrite", _("proj_overwrite")),
            ("cancel", _("proj_cancel")),
        ])
        if choice != "overwrite":
            return

    # Detect tech stack
    detectors = {
        "pyproject.toml": "Python",
        "setup.py": "Python",
        "requirements.txt": "Python",
        "Cargo.toml": "Rust",
        "go.mod": "Go",
        "package.json": "Node.js",
        "tsconfig.json": "TypeScript",
        "CMakeLists.txt": "C/C++ (CMake)",
        "Makefile": "C/C++ (Make)",
        "Dockerfile": "Docker",
        "docker-compose.yml": "Docker Compose",
    }

    stack = []
    for filename, label in detectors.items():
        if (cwd / filename).exists():
            stack.append(label)
    if not stack:
        stack.append("Unknown")

    # Read metadata
    name = cwd.name
    desc = ""

    if (cwd / "pyproject.toml").exists():
        try:
            for line in (cwd / "pyproject.toml").read_text(encoding="utf-8").split("\n"):
                line = line.strip()
                if line.startswith("name "):
                    name = line.split("=", 1)[1].strip().strip("\"'")
                if line.startswith("description "):
                    desc = line.split("=", 1)[1].strip().strip("\"'")
        except (OSError, PermissionError, UnicodeDecodeError):
            pass

    if not desc and (cwd / "package.json").exists():
        try:
            import json
            pkg = json.loads((cwd / "package.json").read_text(encoding="utf-8"))
            name = pkg.get("name", name)
            desc = pkg.get("description", desc) or ""
        except (OSError, PermissionError, json.JSONDecodeError, ValueError):
            pass

    if not desc and (cwd / "README.md").exists():
        try:
            for line in (cwd / "README.md").read_text(encoding="utf-8").split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    desc = line[:120]
                    break
        except (OSError, PermissionError, UnicodeDecodeError):
            pass

    # Detect commands
    build_cmd = ""
    test_cmd = ""
    run_cmd = ""

    if (cwd / "pyproject.toml").exists():
        build_cmd = "pip install -e ."
        test_cmd = "pytest"
    elif (cwd / "package.json").exists():
        build_cmd = "npm install"
        test_cmd = "npm test"
        run_cmd = "npm start"
    elif (cwd / "Cargo.toml").exists():
        build_cmd = "cargo build"
        test_cmd = "cargo test"
        run_cmd = "cargo run"
    elif (cwd / "go.mod").exists():
        build_cmd = "go build ./..."
        test_cmd = "go test ./..."
        run_cmd = "go run ."
    elif (cwd / "Makefile").exists():
        build_cmd = "make"
        test_cmd = "make test"

    # Build document
    lines = [
        f"# {name}",
        "",
        "## Overview",
        f"{desc or 'Project description (edit this)'}",
        "",
        "## Tech Stack",
        ", ".join(f"**{s}**" for s in stack),
        "",
        "## Commands",
    ]
    if build_cmd:
        lines.append(f"- Build: `{build_cmd}`")
    if test_cmd:
        lines.append(f"- Test: `{test_cmd}`")
    if run_cmd:
        lines.append(f"- Run: `{run_cmd}`")

    lines += [
        "",
        "## Directory Structure",
        "",
        "```",
        build_project_tree(max_depth=2),
        "```",
        "",
        "## Conventions",
        "(Edit this section with project-specific conventions, coding style, etc.)",
        "",
        "## Notes",
        f"Generated by FluxLite /init on {datetime.now().strftime('%Y-%m-%d %H:%M')}.",
    ]

    content = "\n".join(lines) + "\n"
    try:
        target.write_text(content, encoding="utf-8")
    except (OSError, PermissionError):
        console.print(f"  [red]{_('proj_write_failed')}[/]")
        return
    console.print(f"  [green]{_('proj_generated_ok', len=len(content))}[/]")
    console.print(f"  [dim]Edit: {target}[/]")
    console.print(f"  [dim]{_('proj_restart_hint')}[/]")
