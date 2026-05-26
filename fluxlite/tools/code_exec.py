"""Code execution tool with auto-linting and auto-fix for Python.

Supports arbitrary shell commands (npm, cargo, go, curl, etc.)."""
import subprocess
import sys
import ast
import re
import tempfile
import difflib
from pathlib import Path

from ..i18n import _
from .sandbox import _SandboxState

DESTRUCTIVE_PATTERNS = [
    re.compile(r'\bshutdown\b'),
    re.compile(r'\breboot\b'),
    re.compile(r'\bhalt\b'),
    re.compile(r'\bpoweroff\b'),
    re.compile(r'\bmkfs\b'),
    re.compile(r'\bdd\s+if='),
    re.compile(r':\s*\(\s*\)\s*\{'),
    re.compile(r'\brm\s+-(?:rf|fr|r\s+-\s*f)\s+[/~.]'),
    re.compile(r'\bdel\s+/[FfQq].*\b'),
    re.compile(r'\brd\s+/[SsQq].*\b'),
    re.compile(r'\bformat\s+[A-Za-z]:'),
    re.compile(r'>\s*/dev/sd'),
    re.compile(r'\bchmod\s+.*777\s+/'),
]

MAX_OUTPUT_LINES = 2000
DEFAULT_TIMEOUT = 30


def _check_blocked(code: str) -> bool:
    for pattern in DESTRUCTIVE_PATTERNS:
        if pattern.search(code):
            return True
    return False


def _run_lint(code: str) -> str:
    issues = []

    try:
        ast.parse(code)
    except SyntaxError as e:
        return f"[lint] SyntaxError: {e}"

    try:
        compile(code, "<check>", "exec")
    except SyntaxError as e:
        issues.append(f"[lint] SyntaxError: {e}")
    except ValueError as e:
        issues.append(f"[lint] ValueError: {e}")

    for linter, cmd in [
        ("pyflakes", [sys.executable, "-m", "pyflakes", "-"]),
        ("pyright", ["pyright", "--outputjson", "-"]),
        ("mypy", [sys.executable, "-m", "mypy", "--ignore-missing-imports", "-"]),
    ]:
        try:
            r = subprocess.run(
                cmd,
                input=code,
                capture_output=True, encoding="utf-8", errors="replace", timeout=10,
            )
            stderr = (r.stderr or "").strip()
            stdout = (r.stdout or "").strip()
            if stderr:
                for line in stderr.split("\n")[:8]:
                    issues.append(f"[{linter}] {line}")
            if stdout:
                for line in stdout.split("\n")[:8]:
                    issues.append(f"[{linter}] {line}")
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            pass

    if not issues:
        return _("exec_lint_ok")
    return "\n".join(issues[:12])


def _auto_fix_code(code: str) -> tuple[str, str]:
    """Attempt to auto-fix Python code using available formatters/linters.
    Returns (fixed_code, report)."""
    fixers = [
        ("ruff", [sys.executable, "-m", "ruff", "check", "--fix", "--stdin-filename", "_.py", "-"],
         True),  # stdin mode
        ("ruff format", [sys.executable, "-m", "ruff", "format", "--stdin-filename", "_.py", "-"],
         True),
        ("autopep8", [sys.executable, "-m", "autopep8", "-"], True),
        ("black", [sys.executable, "-m", "black", "-q", "-"], True),
    ]

    for name, cmd, use_stdin in fixers:
        try:
            r = subprocess.run(
                cmd,
                input=code,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
            )
        except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
            continue

        if r.returncode == 0 and r.stdout and r.stdout.strip():
            fixed = r.stdout.strip()
            if fixed != code.strip():
                diff = list(difflib.unified_diff(
                    code.strip().split("\n"),
                    fixed.split("\n"),
                    fromfile="before",
                    tofile=f"after ({name})",
                    lineterm="",
                ))
                diff_str = "\n".join(diff[:20]) if diff else "(no diff)"
                return fixed, f"[auto-fix] {name} applied\n{diff_str}"
        elif r.returncode == 0 and not (r.stdout or "").strip():
            # Formatter may write to stdout only when changes are made
            # Try with temp file for formatters like black that write in-place
            if not use_stdin:
                continue
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False, encoding="utf-8"
                ) as f:
                    f.write(code)
                    tmp = f.name
                r2 = subprocess.run(
                    cmd[:-1] + [tmp] if use_stdin else cmd + [tmp],
                    capture_output=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=15,
                )
                result = Path(tmp).read_text(encoding="utf-8")
                Path(tmp).unlink(missing_ok=True)
                if result != code:
                    diff = list(difflib.unified_diff(
                        code.strip().split("\n"),
                        result.strip().split("\n"),
                        fromfile="before",
                        tofile=f"after ({name})",
                        lineterm="",
                    ))
                    diff_str = "\n".join(diff[:20]) if diff else "(no diff)"
                    return result, f"[auto-fix] {name} applied\n{diff_str}"
            except (OSError, Exception):
                try:
                    Path(tmp).unlink(missing_ok=True)
                except OSError:
                    pass
                continue

    return code, "[auto-fix] No fixer available or no changes needed"


def execute(language: str, code: str, workdir: str = None, timeout: int = None, lint_fix: bool = False) -> str:
    if _check_blocked(code):
        return _("exec_blocked")

    exec_timeout = timeout or DEFAULT_TIMEOUT
    if workdir:
        cwd = workdir
    else:
        cwd = str(_SandboxState.get_sandbox_dir()) if _SandboxState.is_active() else None

    output_parts = []

    if language == "python":
        try:
            ast.parse(code)
        except SyntaxError as e:
            return _("exec_syntax_error", e=e)

        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=exec_timeout,
                cwd=cwd,
            )
        except subprocess.TimeoutExpired:
            return _("exec_timed_out", timeout=exec_timeout)
        except Exception as e:
            return _("exec_error", e=e)

        if result.stdout:
            lines = result.stdout.rstrip().split("\n")
            if len(lines) > MAX_OUTPUT_LINES:
                lines = lines[:MAX_OUTPUT_LINES]
                lines.append(_("exec_output_truncated", n=len(lines) - MAX_OUTPUT_LINES))
            output_parts.append("[output]\n" + "\n".join(lines))

        if result.stderr:
            lines = result.stderr.rstrip().split("\n")
            if len(lines) > MAX_OUTPUT_LINES:
                lines = lines[:MAX_OUTPUT_LINES]
                lines.append(_("exec_output_truncated", n=len(lines) - MAX_OUTPUT_LINES))
            output_parts.append("[stderr]\n" + "\n".join(lines))

        if result.returncode != 0:
            output_parts.append(_("exec_exit_code", code=result.returncode))

        if not output_parts:
            output_parts.append(_("exec_no_output"))

        lint = _run_lint(code)
        output_parts.append(f"\n[lint]\n{lint}")

        if lint_fix and lint != _("exec_lint_ok"):
            fixed_code, fix_report = _auto_fix_code(code)
            if fixed_code != code:
                output_parts.append(f"\n{fix_report}")
                # Re-run fixed code
                try:
                    r2 = subprocess.run(
                        [sys.executable, "-c", fixed_code],
                        capture_output=True,
                        encoding="utf-8",
                        errors="replace",
                        timeout=exec_timeout,
                        cwd=cwd,
                    )
                    if r2.stdout:
                        output_parts.append("[re-run output]\n" + r2.stdout.rstrip()[:2000])
                    if r2.stderr:
                        output_parts.append("[re-run stderr]\n" + r2.stderr.rstrip()[:1000])
                    if r2.returncode != 0:
                        output_parts.append(f"[re-run] Exit code: {r2.returncode}")
                    else:
                        output_parts.append("[re-run] OK")
                except (subprocess.TimeoutExpired, Exception) as e:
                    output_parts.append(f"[re-run] Error: {e}")
            else:
                output_parts.append(f"\n{fix_report}")

    elif language in ("bash", "shell"):
        try:
            result = subprocess.run(
                code,
                shell=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=exec_timeout,
                cwd=cwd,
            )
        except subprocess.TimeoutExpired:
            return _("exec_timed_out", timeout=exec_timeout)
        except Exception as e:
            return _("exec_error", e=e)

        if result.stdout:
            lines = result.stdout.rstrip().split("\n")
            if len(lines) > MAX_OUTPUT_LINES:
                lines = lines[:MAX_OUTPUT_LINES]
                lines.append(_("exec_output_truncated", n=len(lines) - MAX_OUTPUT_LINES))
            output_parts.append("[output]\n" + "\n".join(lines))

        if result.stderr:
            lines = result.stderr.rstrip().split("\n")
            if len(lines) > MAX_OUTPUT_LINES:
                lines = lines[:MAX_OUTPUT_LINES]
                lines.append(_("exec_output_truncated", n=len(lines) - MAX_OUTPUT_LINES))
            output_parts.append("[stderr]\n" + "\n".join(lines))

        if result.returncode != 0:
            output_parts.append(_("exec_exit_code", code=result.returncode))

        if not output_parts:
            output_parts.append(_("exec_no_output"))

    else:
        return _("exec_unsupported_lang", lang=language)

    return "\n".join(output_parts)
