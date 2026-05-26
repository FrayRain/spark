"""Plugin manager — discover, load, and manage FluxLite plugins.

Plugin structure (~/.fluxlite/plugins/<name>/):
  <name>.json   — metadata + tool schema definitions
  <name>.py     — handler functions (one per tool)
"""

import os
import sys
import json
import types
import shutil
import threading
import importlib.util
from pathlib import Path
from dataclasses import dataclass
from .i18n import _


PLUGINS_DIR = Path.home() / ".fluxlite" / "plugins"
_STATE_FILE = Path.home() / ".fluxlite" / "plugin_state.json"

_lock = threading.Lock()
_plugins: dict[str, dict] = {}
_state: dict[str, bool] = {}


@dataclass
class PluginToolDef:
    name: str
    description: str
    parameters: dict
    handler: callable


def _load_state():
    global _state
    try:
        if _STATE_FILE.exists():
            _state = json.loads(_STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, PermissionError):
        _state = {}


def _save_state():
    try:
        _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _STATE_FILE.write_text(json.dumps(_state, ensure_ascii=False, indent=2), encoding="utf-8")
    except (OSError, PermissionError, TypeError):
        pass


def discover():
    global _plugins
    _load_state()

    plugins = {}
    if not PLUGINS_DIR.is_dir():
        _plugins = plugins
        return

    for folder in sorted(PLUGINS_DIR.iterdir()):
        if not folder.is_dir() or folder.name.startswith("."):
            continue
        info = _load_single_plugin(folder)
        if info:
            plugins[folder.name] = info

    _plugins = plugins


def _load_single_plugin(folder: Path) -> dict | None:
    name = folder.name
    json_path = folder / f"{name}.json"
    py_path = folder / f"{name}.py"

    if not json_path.exists():
        return None

    try:
        meta = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return _error_plugin(name, f"Invalid JSON: {e}")
    except Exception as e:
        return _error_plugin(name, str(e))

    if not isinstance(meta, dict):
        return _error_plugin(name, "JSON root must be an object")
    if not meta.get("tools"):
        return _error_plugin(name, "No tools defined in JSON")

    if not py_path.exists():
        return _error_plugin(name, f"Missing {name}.py")

    module = _import_module(name, py_path)
    if module is None:
        return _error_plugin(name, f"Failed to import {name}.py")

    tools = []
    for tdef in meta["tools"]:
        if not isinstance(tdef, dict) or not tdef.get("name"):
            continue
        func_name = tdef["name"]
        handler = getattr(module, func_name, None)
        if handler is None:
            tools.append(_error_tool(func_name, f"Handler '{func_name}' not found in {name}.py"))
            continue
        if not callable(handler):
            tools.append(_error_tool(func_name, f"'{func_name}' is not callable"))
            continue

        tools.append(PluginToolDef(
            name=f"plugin_{name}_{func_name}",
            description=f"[{name}] {tdef.get('description', '')}",
            parameters=tdef.get("parameters", {}),
            handler=_wrap_handler(name, func_name, handler),
        ))

    enabled = _state.get(name, True)
    return {
        "name": name,
        "meta": meta,
        "module": module,
        "tools": tools,
        "enabled": enabled,
        "error": None,
    }


def _import_module(name: str, py_path: Path):
    """Import a .py file as a module. Supports re-import for hot-reload."""
    try:
        source = py_path.read_text(encoding="utf-8")
        full_name = f"__plugins__.{name}"
        # Remove cached module to support re-import
        if full_name in sys.modules:
            del sys.modules[full_name]
        # Use compile+exec instead of importlib to bypass bytecode caching
        code = compile(source, str(py_path), "exec")
        mod = types.ModuleType(full_name)
        mod.__file__ = str(py_path)
        mod.__spec__ = None
        exec(code, mod.__dict__)
        sys.modules[full_name] = mod
        return mod
    except Exception:
        return None


def _wrap_handler(plugin_name: str, func_name: str, handler: callable):
    def _wrapped(**kwargs):
        try:
            return handler(kwargs)
        except Exception as e:
            return f"[Plugin {plugin_name}] Error in {func_name}: {e}"
    _wrapped.__name__ = func_name
    return _wrapped


def _error_plugin(name: str, error: str) -> dict:
    return {
        "name": name,
        "meta": {"name": name, "version": "?", "description": f"[load error]" },
        "module": None,
        "tools": [],
        "enabled": False,
        "error": error,
    }


def _error_tool(name: str, error: str) -> PluginToolDef:
    return PluginToolDef(
        name=f"plugin_error_{name}",
        description=f"[BROKEN] {error}",
        parameters={},
        handler=lambda args: f"[Plugin Error] {error}",
    )


# ---------------------------------------------------------------------------
# Hot-reload — background file watcher
# ---------------------------------------------------------------------------

_plugin_mtimes: dict[str, dict[str, float]] = {}
_hot_reload_running = False


def start_hot_reload(interval: float = 2.0):
    """Start background thread that watches plugin files for changes."""
    global _hot_reload_running, _plugin_mtimes
    if _hot_reload_running:
        return
    _plugin_mtimes = _get_plugin_mtimes()
    _hot_reload_running = True
    t = threading.Thread(target=_hot_reload_worker, args=(interval,), daemon=True)
    t.start()


def stop_hot_reload():
    global _hot_reload_running
    _hot_reload_running = False


def _hot_reload_worker(interval: float):
    while _hot_reload_running:
        import time as _time
        _time.sleep(interval)
        if not _hot_reload_running:
            break
        try:
            _check_plugin_changes()
        except Exception:
            pass  # Don't crash the background thread


def _get_plugin_mtimes() -> dict[str, dict[str, float]]:
    """Snapshot current mtimes of all plugin .json and .py files."""
    result: dict[str, dict[str, float]] = {}
    if not PLUGINS_DIR.is_dir():
        return result
    for folder in sorted(PLUGINS_DIR.iterdir()):
        if not folder.is_dir() or folder.name.startswith("."):
            continue
        name = folder.name
        files: dict[str, float] = {}
        for fname in (f"{name}.json", f"{name}.py"):
            fp = folder / fname
            if fp.exists():
                try:
                    files[str(fp)] = fp.stat().st_mtime
                except OSError:
                    pass
        if files:
            result[name] = files
    return result


def _reload_single_plugin(name: str) -> dict | None:
    """Reload one plugin by name. Caller must hold _lock."""
    folder = PLUGINS_DIR / name
    if not folder.is_dir():
        _plugins.pop(name, None)
        return None
    info = _load_single_plugin(folder)
    if info:
        _plugins[name] = info
    return info


def _check_plugin_changes():
    """Compare current mtimes with snapshot — reload anything that changed."""
    global _plugin_mtimes
    current = _get_plugin_mtimes()
    all_names = set(current) | set(_plugin_mtimes)

    for name in all_names:
        old = _plugin_mtimes.get(name)
        new = current.get(name)

        # Plugin directory removed
        if old and not new:
            with _lock:
                _plugins.pop(name, None)
            print(f"\n[Plugin] '{name}' removed", file=sys.stderr)
            continue

        # New plugin appeared
        if not old and new:
            with _lock:
                info = _reload_single_plugin(name)
            if info and info.get("error"):
                print(f"\n[Plugin] '{name}' loaded with errors: {info['error']}", file=sys.stderr)
            else:
                print(f"\n[Plugin] '{name}' loaded", file=sys.stderr)
            _plugin_mtimes[name] = new
            continue

        # Existing plugin changed
        if old and new and old != new:
            with _lock:
                info = _reload_single_plugin(name)
            if info and info.get("error"):
                print(f"\n[Plugin] '{name}' hot-reloaded with errors: {info['error']}", file=sys.stderr)
            else:
                print(f"\n[Plugin] '{name}' hot-reloaded", file=sys.stderr)
            _plugin_mtimes[name] = new

    _plugin_mtimes = current


def get_plugin_tools() -> list[PluginToolDef]:
    with _lock:
        tools = []
        for name, info in _plugins.items():
            if not info.get("enabled"):
                continue
            tools.extend(info.get("tools", []))
        return tools


def get_tool_schemas() -> list[dict]:
    schemas = []
    for tool in get_plugin_tools():
        schemas.append({
            "name": tool.name,
            "description": tool.description,
            "parameters": dict(tool.parameters),
        })
    return schemas


def list_plugins() -> str:
    with _lock:
        if not _plugins:
            return _("plugin_no_plugins")

        lines = [f"Plugins ({len(_plugins)}):"]
        for name, info in _plugins.items():
            meta = info.get("meta", {})
            ver = meta.get("version", "?")
            desc = meta.get("description", "")
            err = info.get("error")
            enabled = info.get("enabled", False)
            status = "enabled" if enabled else "disabled"
            if err:
                status = "error"
            tool_count = len(info.get("tools", []))
            lines.append(f"  [{status}] {name} v{ver} — {desc} ({tool_count} tools)")
            if err:
                lines.append(f"    Error: {err}")
        return "\n".join(lines)


def plugin_info(name: str) -> str:
    with _lock:
        info = _plugins.get(name)
        if not info:
            return _("plugin_not_found", name=name)

        meta = info.get("meta", {})
        lines = [
            f"Name: {meta.get('name', name)}",
            f"Version: {meta.get('version', '?')}",
            f"Author: {meta.get('author', '?')}",
            f"Website: {meta.get('website', '')}",
            f"Description: {meta.get('description', '')}",
            f"Enabled: {info.get('enabled', False)}",
        ]
        err = info.get("error")
        if err:
            lines.append(f"Error: {err}")
        lines.append("")
        lines.append("Tools:")
        for tool in info.get("tools", []):
            params = ", ".join(tool.parameters.keys()) if tool.parameters else "(no params)"
            lines.append(f"  {tool.name}({params}) — {tool.description}")
        return "\n".join(lines)


def enable_plugin(name: str) -> str:
    with _lock:
        if name not in _plugins:
            return _("plugin_not_found", name=name)
        if _plugins[name].get("error"):
            return f"Plugin '{name}' has errors and cannot be enabled: {_plugins[name]['error']}"
        _plugins[name]["enabled"] = True
        _state[name] = True
        _save_state()
        return _("plugin_enabled_ok", name=name)


def disable_plugin(name: str) -> str:
    with _lock:
        if name not in _plugins:
            return _("plugin_not_found", name=name)
        _plugins[name]["enabled"] = False
        _state[name] = False
        _save_state()
        return _("plugin_disabled_ok", name=name)


def reload_plugins():
    global _plugin_mtimes
    with _lock:
        discover()
    _plugin_mtimes = _get_plugin_mtimes()
    return _("plugin_reloaded")


def create_plugin(name: str) -> str:
    plugin_dir = PLUGINS_DIR / name
    if plugin_dir.exists():
        return _("plugin_already_exists", name=name, dir=str(plugin_dir))

    if not name.isidentifier():
        return _("plugin_invalid_name", name=name)

    plugin_dir.mkdir(parents=True, exist_ok=True)

    json_content = {
        "name": name,
        "version": "1.0.0",
        "description": "Describe your plugin here",
        "author": "Your Name",
        "website": "",
        "tools": [
            {
                "name": "hello",
                "description": "Say hello - example tool with optional parameter",
                "parameters": {
                    "name": {
                        "type": "string",
                        "desc": "Name to greet",
                        "optional": True,
                    }
                },
            },
            {
                "name": "echo",
                "description": "Echo back what you say - shows required + optional params",
                "parameters": {
                    "message": {
                        "type": "string",
                        "desc": "Message to echo",
                    },
                    "times": {
                        "type": "number",
                        "desc": "Repeat count (1-10)",
                        "optional": True,
                    },
                    "shout": {
                        "type": "boolean",
                        "desc": "UPPERCASE the message",
                        "optional": True,
                    },
                },
            },
        ],
    }

    (plugin_dir / f"{name}.json").write_text(
        json.dumps(json_content, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    py_content = f'''"""{name} plugin -- FluxLite

Auto-generated scaffold. Edit the tools in {name}.json and
implement the matching handler functions below.
"""
import os
import json

from fluxlite.plugin_api import (
    PluginError,
    format_result,
    read_file,
    write_file,
    list_dir,
    timestamp,
    uuid_gen,
)


# ---------------------------------------------------------------------------
# Storage helpers — data dir lives under ~/.fluxlite/plugins_data/{name}/
# ---------------------------------------------------------------------------

DATA_DIR = os.path.expanduser(f"~/.fluxlite/plugins_data/{name}")


def _ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def _data_path(key: str) -> str:
    return os.path.join(DATA_DIR, f"{{key}}.json")


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------


def hello(args: dict) -> str:
    \"\"\"Say hello to someone.

    Every handler receives a single ``args`` dict with keys matching the
    parameters declared in {name}.json.  Raise ``PluginError`` for invalid
    input; return a string (use ``format_result()`` for structured data).
    \"\"\"
    name = args.get("name", "World")
    return format_result({{
        "message": f"Hello, {{name}}!",
        "plugin": "{name}",
    }})


def echo(args: dict) -> str:
    \"\"\"Echo back a message, optionally repeated or uppercased.\"\"\"
    message = args.get("message")
    if not message or not message.strip():
        raise PluginError("message is required")

    times = int(args.get("times", 1))
    if times < 1 or times > 10:
        raise PluginError("times must be between 1 and 10")

    if args.get("shout", False):
        message = message.upper()

    lines = [message] * times
    return format_result({{
        "original": args.get("message"),
        "echoed": lines,
        "count": times,
        "shout": args.get("shout", False),
    }})
'''
    (plugin_dir / f"{name}.py").write_text(py_content, encoding="utf-8")

    return (
        f"Plugin '{name}' scaffolded at {plugin_dir}\n"
        f"  {name}.json  — tool definitions (edit to add/change tools)\n"
        f"  {name}.py    — handler implementations (one function per tool)\n"
        f"\n"
        f"Next steps:\n"
        f"  1. Edit {name}.json to describe your tools\n"
        f"  2. Implement each tool function in {name}.py\n"
        f"  3. Changes auto-load (hot-reload active)"
    )
