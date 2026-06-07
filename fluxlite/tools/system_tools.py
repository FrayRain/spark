"""System tools: process listing and application launching."""
import os
import subprocess
import sys
from ..i18n import _


def list_processes(sort_by: str = "name", name_filter: str = "") -> str:
    """List running processes with PID, name, and memory usage."""
    import psutil

    sort_by = (sort_by or "name").lower()
    processes = []
    for proc in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            info = proc.info
            name = (info["name"] or "")
            if name_filter and name_filter.lower() not in name.lower():
                continue
            mem = info["memory_info"].rss / 1024 / 1024 if info["memory_info"] else 0
            processes.append((name, info["pid"], mem))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    if sort_by == "memory":
        processes.sort(key=lambda x: x[2], reverse=True)
    elif sort_by == "pid":
        processes.sort(key=lambda x: x[1])
    else:
        processes.sort(key=lambda x: x[0].lower())

    lines = [f"{'PID':>7} {'MEM(MB)':>9}  NAME"]
    for name, pid, mem in processes[:80]:
        lines.append(f"{pid:>7} {mem:>8.1f}  {name}")

    total = len(processes)
    if name_filter:
        total_all = len(list(psutil.process_iter(["pid"])))
        lines.append(f"\n{total} matching (of {total_all} total)")
    else:
        lines.append(f"\n{total} processes")
    return "\n".join(lines)


def launch_app(target: str, wait: bool = False) -> str:
    """Launch an application or open a file/URL/directory.

    On Windows uses os.startfile (same as double-click).
    On macOS uses 'open'.
    On Linux uses 'xdg-open'.

    For executable files on any platform, uses subprocess.Popen.
    """
    import subprocess

    if sys.platform == "win32":
        ext = os.path.splitext(target)[1].lower()
        if ext in (".exe", ".bat", ".cmd", ".com", ".msi"):
            try:
                proc = subprocess.Popen(
                    target,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if wait:
                    proc.wait(timeout=30)
                return _("sys_launched", target=target, pid=proc.pid)
            except FileNotFoundError:
                return _("sys_not_found", target=target)
        else:
            try:
                os.startfile(target)
                return _("sys_opened", target=target)
            except FileNotFoundError:
                return _("sys_not_found", target=target)
            except OSError as e:
                return _("sys_launch_error", target=target, error=e)
    elif sys.platform == "darwin":
        try:
            proc = subprocess.Popen(
                ["open", target],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if wait:
                proc.wait(timeout=30)
            return _("sys_opened", target=target)
        except FileNotFoundError:
            return _("sys_not_found", target=target)
        except OSError as e:
            return _("sys_launch_error", target=target, error=e)
    else:
        try:
            proc = subprocess.Popen(
                ["xdg-open", target],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if wait:
                proc.wait(timeout=30)
            return _("sys_opened", target=target)
        except FileNotFoundError:
            return _("sys_not_found", target=target)
        except OSError as e:
            return _("sys_launch_error", target=target, error=e)
