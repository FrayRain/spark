import difflib
import json
import os
import shlex
from datetime import datetime
from pathlib import Path

from .i18n import _, set_lang
from .styles import CYAN, GREEN, PURPLE, ORANGE, RED, GRAY, DIM, BLUE
from .provider import detect_provider_type
from .tools.registry import TOOLS
from .profile import load_profile, save_profile, add_rule as profile_add_rule
from .startup import print_header
from .memory import load_memories, save_memories
from .console import console, get_input, radio_select


MODEL_PRESETS = {
    "deepseek": [
        ("1", "DeepSeek V4 Flash", "deepseek-v4-flash"),
        ("2", "DeepSeek V4 Pro", "deepseek-v4-pro"),
        ("3", "DeepSeek Chat", "deepseek-chat"),
        ("4", "DeepSeek Reasoner", "deepseek-reasoner"),
    ],
    "openai": [
        ("1", "GPT-4o", "gpt-4o"),
        ("2", "GPT-4o Mini", "gpt-4o-mini"),
        ("3", "GPT-4 Turbo", "gpt-4-turbo"),
        ("4", "GPT-3.5 Turbo", "gpt-3.5-turbo"),
    ],
    "openrouter": [
        ("1", "OpenAI GPT-4o", "openai/gpt-4o"),
        ("2", "Claude 3.5 Sonnet", "anthropic/claude-3.5-sonnet"),
        ("3", "Gemini 2.0 Flash", "google/gemini-2.0-flash"),
        ("4", "DeepSeek V4", "deepseek/deepseek-chat"),
    ],
    "groq": [
        ("1", "Llama 3.3 70B", "llama-3.3-70b-versatile"),
        ("2", "Mixtral 8x7B", "mixtral-8x7b-32768"),
        ("3", "Gemma2 9B", "gemma2-9b-it"),
    ],
    "anthropic": [
        ("1", "Claude Sonnet 4", "claude-sonnet-4-20250514"),
        ("2", "Claude Haiku 3.5", "claude-3-5-haiku-latest"),
        ("3", "Claude Opus 4", "claude-opus-4-20250514"),
        ("4", "Claude Sonnet 4 (1M ctx)", "claude-sonnet-4-1m"),
        ("5", "Claude Opus 4 (1M ctx)", "claude-opus-4-1m"),
    ],
}


def show_memory():
    profile = load_profile()
    identity = profile.get("identity", {})
    console.print(f"\n  [{CYAN}]{_('identity_title')}[/]")
    if identity.get("name"):
        console.print(f"    {_('memory_name')} {identity['name']}")
    if identity.get("user_name"):
        console.print(f"    {_('memory_user')} {identity['user_name']}")
    if identity.get("personality"):
        console.print(f"    {_('memory_personality')} {identity['personality']}")

    rules = profile.get("rules", [])
    if rules:
        console.print(f"\n  [{ORANGE}]Rules ({len(rules)})[/]")
        for i, r in enumerate(rules):
            console.print(f"    {i+1}. {r}")
    else:
        console.print(f"\n  [{GRAY}]{_('memory_no_rules')}[/]")

    entries = load_memories()
    if entries:
        console.print(f"\n  [{PURPLE}]Memories ({len(entries)})[/]")
        for m in entries[-5:]:
            console.print(f"    {m.get('content', '')[:80]}")
    console.print()


def _handle_summarize(messages: list, provider, _desc: str):
    """Summarize current conversation and save as memory."""
    _ = _desc  # suppress lint
    from .memory import summarize_conversation
    console.print(f"\n  [{GRAY}]{_('memory_summarizing')}[/]")
    summary = summarize_conversation(messages, provider, "zh")
    if summary:
        console.print(f"  [{PURPLE}]{_('memory_summary_saved')}[/]")
        for line in summary.split("\n"):
            console.print(f"    {line}")
    else:
        console.print(f"  [{ORANGE}]{_('memory_too_few')}[/]")


def compact_memory():
    entries = load_memories()
    if len(entries) < 3:
        console.print(f"  [{GRAY}]{_('memory_already_compact', count=len(entries))}[/]")
        return
    summary = "\n".join(f"- {e['content']}" for e in entries)
    compacted = {
        "id": "compact",
        "content": f"Consolidated memory:\n{summary}",
        "created_at": datetime.now().isoformat(),
    }
    save_memories([compacted])
    console.print(f"  [{PURPLE}]{_('compact_done')} ({len(entries)} entries compacted)[/]")


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        pass
    import unicodedata
    cjk = sum(1 for c in text if "CJK" in unicodedata.name(c, "") or
              "一" <= c <= "鿿" or "　" <= c <= "〿")
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    other = len(text) - cjk - ascii_chars
    return max(1, cjk * 2 + ascii_chars // 4 + other // 3)


def perform_rewind(messages: list) -> bool:
    for i in range(len(messages) - 1, -1, -1):
        if messages[i]["role"] == "user":
            del messages[i:]
            return True
    return False


class CommandState:
    thinking_mode = "off"
    reasoning_effort = ""  # "", "low", "medium", "high"
    auto_debug = True
    show_tool_result = False
    show_token_usage = False
    new_session_requested = False
    session_load_requested = False
    session_load_data = None
    git_autocommit = False
    pinned_files: set = set()

    _SETTINGS_KEYS = [
        "thinking_mode", "reasoning_effort", "auto_debug",
        "show_tool_result", "show_token_usage", "git_autocommit",
    ]

    @classmethod
    def load_from_settings(cls):
        from .profile import load_settings
        settings = load_settings()
        for key in cls._SETTINGS_KEYS:
            if key in settings:
                setattr(cls, key, settings[key])

    @classmethod
    def save(cls):
        from .profile import save_settings
        settings = {key: getattr(cls, key) for key in cls._SETTINGS_KEYS}
        save_settings(settings)

    @classmethod
    def reset_pins(cls):
        cls.pinned_files = set()


def handle_command(cmd: str, messages: list, model: str, provider, context_extra: dict = None):
    state = CommandState
    cmd = cmd.lower().strip()

    # Short aliases
    _aliases = {"/s": "/sessions", "/p": "/plan", "/c": "/compact", "/q": "/exit"}
    if cmd in _aliases:
        cmd = _aliases[cmd]

    if cmd in ("/help", "/h"):
        console.print()
        console.print(f"  [{CYAN}]\u2501 Commands[/]")
        console.print(f"    [{GREEN}]/help[/]         {_('help_desc')}")
        console.print(f"    [{GREEN}]/clear[/]        {_('clear_desc')}")
        console.print(f"    [{GREEN}]/model[/]        {_('model_desc')}")
        console.print(f"    [{GREEN}]/memory[/]       {_('show_memory')}")
        console.print(f"    [{GREEN}]/think[/]        {_('think_desc')}")
        console.print(f"    [{GREEN}]/compact[/]      {_('compact_desc')}")
        console.print(f"    [{GREEN}]/summarize[/]    {_('summarize_desc')}")
        console.print(f"    [{GREEN}]/toolresult[/]   {_('toolresult_desc')}")
        console.print(f"    [{GREEN}]/export[/]       {_('export_desc')}")
        console.print(f"    [{GREEN}]/token[/]        {_('token_desc')}")
        console.print(f"    [{GREEN}]/truncate[/]     {_('truncate_desc')}")
        console.print(f"    [{GREEN}]/rewind[/]      {_('rewind_desc')}")
        console.print(f"    [{GREEN}]/context[/]     {_('context_desc')}")
        console.print(f"    [{GREEN}]/rule <text>[/]  {_('rule_desc')}")
        console.print(f"    [{GREEN}]/tools[/]        {_('tools_desc')}")
        console.print(f"    [{GREEN}]/lang[/]         {_('lang_desc')}")
        console.print(f"    [{GREEN}]/git[/]          {_('git_desc')}")
        console.print(f"    [{GREEN}]/autocommit[/]   {_('autocommit_desc')}")
        console.print(f"    [{GREEN}]/autodebug[/]   {_('autodebug_desc')}")
        console.print(f"    [{GREEN}]/exit[/]         {_('exit_desc')}")
        console.print(f"    [{GREEN}]/new[/]          {_('new_desc')}")
        console.print(f"    [{GREEN}]/sessions[/]     {_('sessions_desc')}")
        console.print(f"    [{GREEN}]/search[/]      {_('search_desc')}")
        console.print(f"    [{GREEN}]/plan[/]        {_('plan_cmd_desc')}")
        console.print(f"    [{GREEN}]/mcp[/]         {_('mcp_desc')}")
        console.print(f"    [{GREEN}]/knowledge[/]   {_('knowledge_desc')}")
        console.print(f"    [{GREEN}]/hooks[/]       {_('hooks_cmd_desc')}")
        console.print(f"    [{GREEN}]/plugin[/]     {_('plugin_desc')}")
        console.print(f"    [{GREEN}]/sandbox[/]     {_('sandbox_cmd_desc')}")
        console.print(f"    [{GREEN}]/last[/]        {_('last_desc')}")
        console.print(f"    [{GREEN}]/init[/]        {_('init_desc')}")
        console.print(f"    [{GREEN}]/diff[/]        {_('diff_desc')}")
        console.print(f"    [{GREEN}]/review[/]      {_('review_desc')}")
        console.print(f"    [{GREEN}]/fix[/]         {_('fix_cmd_desc')}")
        console.print(f"    [{GREEN}]/pin <file>[/]  {_('pin_desc')}")
        return False

    if cmd == "/last":
        _show_history(messages, context_extra)
        return False

    if cmd == "/clear":
        os.system("cls" if os.name == "nt" else "clear")
        print_header(model=model)
        console.print()
        return False

    if cmd.startswith("/model"):
        provider_key = detect_provider_type(provider._client.base_url)
        presets = MODEL_PRESETS.get(provider_key, [])
        if presets:
            console.print()
            console.print(f"  [{CYAN}]\u2501 {_('cmd_available_models')}[/]")
            for key, label, name in presets:
                marker = "[bold]" if name == provider.model else ""
                console.print(f"    [{GREEN}]{key}[/]) {marker}{label}[/]")
            console.print(f"    [custom] Custom input")
        choice = get_input(f"  {_('cmd_select_model')} ")
        choice = choice.strip()
        if choice == "custom":
            new_model = get_input(f"  {_('cmd_model_name')} ")
            if new_model.strip():
                provider.model = new_model.strip()
                console.print(f"  [{PURPLE}]{_('cmd_model_label')} {provider.model}[/]")
        elif choice and presets:
            for key, label, name in presets:
                if choice == key:
                    provider.model = name
                    console.print(f"  [{PURPLE}]{_('cmd_model_label')} {label} ({name})[/]")
                    break
        return False

    if cmd == "/lang":
        choice = get_input(f"  {_('cmd_lang_prompt')} ")
        choice = choice.strip()
        if choice in ("1", "zh"):
            set_lang("zh")
            console.print(f"  [{CYAN}]lang: zh[/]")
        elif choice in ("2", "en"):
            set_lang("en")
            console.print(f"  [{CYAN}]lang: en[/]")
        return False

    if cmd == "/new":
        state.new_session_requested = True
        console.print(f"  [{GREEN}]{_('main_new_session')}[/]")
        return False

    if cmd == "/sessions":
        _handle_sessions()
        return False

    if cmd in ("/exit", "/quit"):
        console.print(f"\n  [{DIM}]{_('exit')}[/]")
        return True

    if cmd == "/tools":
        console.print()
        console.print(f"  [{ORANGE}]\u2501 {_('cmd_tools_header', count=len(TOOLS))}[/]")
        for t in TOOLS:
            params = ", ".join(t.parameters.keys()) if t.parameters else ""
            console.print(f"    [{GREEN}]{t.name}[/]({params})  [{GRAY}]{_(t.description)[:50]}[/]")
        return False

    if cmd == "/memory":
        show_memory()
        return False

    if cmd == "/compact":
        compact_memory()
        return False

    if cmd == "/summarize":
        _handle_summarize(messages, provider, _("summarize_desc"))
        return False

    if cmd == "/truncate":
        removed = False
        # 1) Remove oldest tool cycle (assistant with tool_calls + tool results)
        for i in range(1, len(messages)):
            if messages[i].get("tool_calls"):
                del messages[i]
                while i < len(messages) and messages[i]["role"] == "tool":
                    del messages[i]
                console.print(f"  [{ORANGE}]! {_('truncate_smart')}[/]")
                removed = True
                break
        # 2) Fallback: remove oldest user+assistant exchange
        if not removed:
            for i in range(1, len(messages) - 1):
                if messages[i]["role"] == "user":
                    del messages[i:i+2]
                    console.print(f"  [{ORANGE}]! {_('truncate_exchange')}[/]")
                    removed = True
                    break
        if not removed:
            console.print(f"  [{GRAY}]{_('cmd_nothing_truncate')}[/]")
        return False

    if cmd.startswith("/rule "):
        rule = cmd[6:].strip()
        if rule:
            profile = load_profile()
            profile_add_rule(profile, rule)
            console.print(f"  [{GREEN}]{_('cmd_rule_recorded')} {rule}[/]")
        return False

    if cmd.startswith("/toolresult"):
        parts = cmd.split()
        if len(parts) >= 2:
            if parts[1] == "on":
                state.show_tool_result = True
                console.print(f"  [{PURPLE}]{_('cmd_toolresult_on')}[/]")
            elif parts[1] == "off":
                state.show_tool_result = False
                console.print(f"  [{GRAY}]{_('cmd_toolresult_off')}[/]")
            state.save()
        return False

    if cmd == "/export":
        export_path = Path.cwd() / f"fluxlite-export-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        try:
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(_('cmd_export_header'))
                for m in messages:
                    role = m.get("role", "")
                    content = m.get("content", "")
                    if role == "system":
                        continue
                    elif role == "user":
                        f.write(f"## User\n\n{content}\n\n")
                    elif role == "assistant":
                        f.write(f"## Assistant\n\n{content}\n\n")
                    elif role == "tool":
                        f.write(f"> Tool result: {content[:200]}\n\n")
            console.print(f"  [{GREEN}]{_('cmd_export_to')} {export_path}[/]")
        except Exception as e:
            console.print(f"  [{RED}]{_('cmd_export_failed')} {e}[/]")
        return False

    if cmd == "/token":
        state.show_token_usage = not state.show_token_usage
        status = "on" if state.show_token_usage else "off"
        console.print(f"  [{'PURPLE' if state.show_token_usage else 'GRAY'}]{_('cmd_token_display')} {status}[/]")
        state.save()
        return False

    if cmd.startswith("/think"):
        parts = cmd.split()
        if len(parts) == 1:
            # Show status
            mode_label = "on" if state.thinking_mode != "off" else "off"
            effort = state.reasoning_effort or "default"
            console.print(f"  [{PURPLE}]{_('think_status', mode=mode_label, effort=effort)}[/]")
        elif len(parts) >= 2:
            sub = parts[1]
            if sub == "on":
                state.thinking_mode = "visible"
                console.print(f"  [{PURPLE}]{_('think_on')}[/]")
            elif sub == "off":
                state.thinking_mode = "off"
                console.print(f"  [{GRAY}]{_('think_off')}[/]")
            elif sub == "effort":
                if len(parts) >= 3:
                    level = parts[2].lower()
                    if level in ("low", "medium", "high"):
                        state.reasoning_effort = level
                        label = _("think_effort_" + level)
                        console.print(f"  [{PURPLE}]{_('think_effort_set', level=label)}[/]")
                    else:
                        console.print(f"  [{ORANGE}]/think effort <low|medium|high>[/]")
                else:
                    current = state.reasoning_effort or "default"
                    console.print(f"  [{PURPLE}]{_('think_effort_current', level=current)}[/]")
                return False
            elif sub == "display":
                if len(parts) >= 3 and parts[2] == "off":
                    if state.thinking_mode != "off":
                        state.thinking_mode = "collapsed"
                    console.print(f"  [{GRAY}]{_('think_display_off')}[/]")
                else:
                    state.thinking_mode = "visible"
                    console.print(f"  [{PURPLE}]{_('think_display_on')}[/]")
            state.save()
        return False

    if cmd == "/autocommit":
        state.git_autocommit = not state.git_autocommit
        status = "on" if state.git_autocommit else "off"
        console.print(f"  [{'PURPLE' if state.git_autocommit else 'GRAY'}]{_('cmd_autocommit_status')} {status}[/]")
        state.save()
        return False

    if cmd == "/autodebug":
        state.auto_debug = not state.auto_debug
        status = "on" if state.auto_debug else "off"
        color = "PURPLE" if state.auto_debug else "GRAY"
        key = "auto_debug_on" if state.auto_debug else "auto_debug_off"
        console.print(f"  [{color}]{_(key)}[/]")
        state.save()
        return False

    if cmd.startswith("/search"):
        keyword = cmd[8:].strip()
        if keyword:
            _handle_search(keyword)
        else:
            keyword = get_input(f"  {_('cmd_search_keyword')} ").strip()
            if keyword:
                _handle_search(keyword)
        return False

    if cmd == "/git":
        _handle_git()
        return False

    if cmd.startswith("/plan"):
        _handle_plan(cmd[6:].strip(), messages)
        return False

    if cmd == "/mcp":
        _handle_mcp()
        return False

    if cmd == "/hooks":
        from .tools.hooks import list_hooks
        console.print(list_hooks())
        return False

    if cmd.startswith("/knowledge"):
        parts = cmd.split()
        sub = parts[1] if len(parts) > 1 else "status"

        from .knowledge import KnowledgeBase
        from .tools.registry import _kb_instance, set_knowledge_base

        kb = _kb_instance or KnowledgeBase(Path.cwd())

        if sub == "build":
            force = "--force" in parts or "-f" in parts
            console.print(f"  [{PURPLE}]{_('know_building')}[/]")
            msg = kb.build(force=force)
            set_knowledge_base(kb)
            console.print(f"  [{GREEN}]{msg}[/]")
        elif sub == "status":
            if not _kb_instance:
                console.print(f"  [{GRAY}]{_('know_not_built')}[/]")
            else:
                console.print(f"  [{CYAN}]{_kb_instance.stats()}[/]")
        elif sub == "search":
            query = " ".join(parts[2:])
            if not query:
                query = get_input(f"  [{CYAN}]Search: [/]").strip()
            if query:
                results = kb.search(query, top_k=5)
                if not results:
                    console.print(f"  [{GRAY}]No matches[/]")
                else:
                    console.print(f"  [{CYAN}]━ Results ({len(results)})[/]")
                    for i, r in enumerate(results, 1):
                        loc = f"{r['file']}:{r['start']}-{r['end']}"
                        console.print(f"  [{GREEN}]{i}. {loc}[/]  score={r['score']}")
                        snippet = r["content"][:200].replace("\n", " ")
                        console.print(f"     [{GRAY}]{snippet}[/]")
        else:
            console.print(f"  {_('know_usage')}")
        return False

    if cmd.startswith("/plugin"):
        from . import plugin_manager
        parts = cmd.split()
        if len(parts) < 2:
            console.print(f"  Usage: /plugin <list|info|enable|disable|create|reload>")
            return False
        sub = parts[1]

        if sub == "list":
            console.print(plugin_manager.list_plugins())
        elif sub == "reload":
            console.print(plugin_manager.reload_plugins())
        elif sub == "info" and len(parts) >= 3:
            console.print(plugin_manager.plugin_info(parts[2]))
        elif sub == "enable" and len(parts) >= 3:
            console.print(plugin_manager.enable_plugin(parts[2]))
        elif sub == "disable" and len(parts) >= 3:
            console.print(plugin_manager.disable_plugin(parts[2]))
        elif sub == "create" and len(parts) >= 3:
            console.print(plugin_manager.create_plugin(parts[2]))
        else:
            console.print(f"  Usage: /plugin <list|info|enable|disable|create|reload>")
        return False

    if cmd.startswith("/sandbox"):
        from .tools.sandbox import _SandboxState
        parts = cmd.split()
        if len(parts) < 2:
            console.print(f"  {_('sandbox_usage')}")
            return False
        sub = parts[1]
        if sub == "on":
            path = _SandboxState.enable()
            console.print(f"  [purple]{_('sandbox_enabled')}[/]  [gray]temp: {path}[/]")
        elif sub == "off":
            _SandboxState.disable()
            console.print(f"  [gray]{_('sandbox_disabled')}[/]")
        elif sub == "status":
            console.print(f"  [cyan]{_SandboxState.status()}[/]")
        elif sub == "review":
            diff = _SandboxState.review()
            console.print(diff if diff else f"  [{GRAY}]{_('sandbox_no_changes')}[/]")
        elif sub == "apply":
            msg = _SandboxState.apply()
            console.print(f"  [green]{msg}[/]")
        elif sub == "discard":
            msg = _SandboxState.discard()
            console.print(f"  [orange]{msg}[/]")
        else:
            console.print(f"  [red]{_('sandbox_unknown_action', action=sub)}[/]")
        return False

    if cmd == "/init":
        from .context import generate_fluxlite_md
        generate_fluxlite_md(console, radio_select)
        return False

    if cmd == "/context":
        parts = cmd.split()
        if len(parts) > 1 and parts[1] == "system":
            sys_content = messages[0].get("content", "") if messages else ""
            if sys_content:
                from rich.markdown import Markdown
                console.print(f"\n  [{CYAN}]━━━ {_('system_size')} ({len(sys_content)} {_('ctx_chars')}) ━━━[/]")
                console.print(f"  [{GRAY}]{sys_content[:3000]}[/]")
                if len(sys_content) > 3000:
                    console.print(f"  [{GRAY}]{_('interrupt_more_chars', n=len(sys_content) - 3000)}[/]")
                console.print()
            else:
                console.print(f"  [{GRAY}]No system prompt[/]")
        else:
            _show_context(messages, model, context_extra or {})
        return False

    if cmd.startswith("/pin"):
        parts = cmd.split()
        if len(parts) >= 2:
            f = parts[1]
            if f in CommandState.pinned_files:
                CommandState.pinned_files.discard(f)
                console.print(f"  [{GRAY}]Unpinned: {f}[/]")
            else:
                CommandState.pinned_files.add(f)
                console.print(f"  [{GREEN}]Pinned: {f}[/]")
        else:
            if CommandState.pinned_files:
                console.print(f"  [{CYAN}]Pinned files:[/]")
                for f in sorted(CommandState.pinned_files):
                    console.print(f"    [{GRAY}]{f}[/]")
            else:
                console.print(f"  [{GRAY}]No pinned files[/]")
        return False

    if cmd == "/diff":
        import subprocess
        try:
            r = subprocess.run(
                ["git", "diff"], capture_output=True, text=True, timeout=10,
                encoding="utf-8", errors="replace",
            )
            out = r.stdout.strip() if r.stdout else ""
            if out:
                console.print(f"  [{CYAN}]━━━ git diff ━━━[/]")
                for line in out.split("\n")[:80]:
                    console.print(f"  [{GRAY}]{line[:100]}[/]")
                if out.count("\n") > 80:
                    console.print(f"  [{GRAY}]... ({out.count(chr(10)) - 80} more lines)[/]")
            else:
                console.print(f"  [{GRAY}]{_('git_no_changes')}[/]")
        except Exception as e:
            console.print(f"  [{RED}]{e}[/]")
        return False

    if cmd == "/review":
        import subprocess
        try:
            r = subprocess.run(
                ["git", "diff", "--cached"], capture_output=True, text=True,
                timeout=10, encoding="utf-8", errors="replace",
            )
            diff = r.stdout.strip() if r.stdout else ""
            if not diff:
                r2 = subprocess.run(
                    ["git", "diff"], capture_output=True, text=True, timeout=10,
                    encoding="utf-8", errors="replace",
                )
                diff = (r2.stdout or "").strip()
            if not diff:
                console.print(f"  [{GRAY}]No changes to review[/]")
                return False
        except Exception as e:
            console.print(f"  [{RED}]{e}[/]")
            return False

        review_prompt = (
            "Review the following code changes. "
            "Identify bugs, style issues, logic errors, and suggest improvements.\n\n"
            f"```diff\n{diff[:4000]}\n```"
        )
        messages.append({"role": "user", "content": review_prompt})
        console.print(f"  [{GREEN}]Review requested ({len(diff)} chars of diff)[/]")
        return False

    if cmd == "/fix":
        # Find last error in conversation
        last_error = ""
        for m in reversed(messages):
            c = m.get("content", "")
            if "error" in c.lower() or "traceback" in c.lower() or "FAIL" in c:
                last_error = c
                break
        if not last_error:
            console.print(f"  [{GRAY}]No recent error found in conversation[/]")
            return False

        fix_prompt = (
            "The following error occurred. Please analyze it and fix the code.\n\n"
            f"Error:\n```\n{last_error[:2000]}\n```"
        )
        messages.append({"role": "user", "content": fix_prompt})
        console.print(f"  [{GRAY}]Analysis request sent[/]")
        return False

    if cmd == "/rewind":
        if perform_rewind(messages):
            console.print(f"  [{PURPLE}]{_('rewind_done')}[/]")
        else:
            console.print(f"  [{GRAY}]Nothing to rewind[/]")
        return False

    # Suggest closest known command
    known = ["help", "clear", "model", "memory", "think", "compact", "toolresult",
             "export", "token", "truncate", "rewind", "context", "tools", "lang",
             "git", "autocommit", "autodebug", "new", "sessions", "search", "last", "plan",
             "mcp", "hooks", "plugin", "sandbox", "exit", "rule",
             "diff", "review", "fix", "pin", "init"]
    cmd_name = cmd.lstrip("/")
    matches = difflib.get_close_matches(cmd_name, known, n=1, cutoff=0.5)
    if matches:
        console.print(f"  [{RED}]x {_('cmd_unknown')}: {cmd}[/]  [{GRAY}]{_('cmd_did_you_mean')} /{matches[0]}?[/]")
    else:
        console.print(f"  [{RED}]x {_('cmd_unknown')}: {cmd}[/]")
    return False


def _show_context(messages: list, model: str, extra: dict):
    """Display current context information."""
    ctx = extra or {}

    # Message counts by role
    counts = {}
    for m in messages:
        role = m["role"]
        counts[role] = counts.get(role, 0) + 1
    total_msgs = len(messages)

    # Token estimates
    sys_prompt = messages[0].get("content", "") if messages else ""
    all_content = " ".join(
        m.get("content", "") for m in messages[1:]
    )
    sys_tokens = estimate_tokens(sys_prompt)
    total_tokens = sys_tokens + estimate_tokens(all_content)

    console.print()
    console.print(f"  [{CYAN}]━ {_('context_title')}[/]")
    console.print(f"    Model:        [{PURPLE}]{model}[/]")
    console.print(f"    {_('msg_count')}:      {total_msgs} {' '.join(f'({r}: {c})' for r, c in counts.items())}")
    console.print(f"    {_('system_size')}: ~{sys_tokens} {_('token_estimate')}")
    console.print(f"    {_('token_estimate')}:  ~{total_tokens} {_('ctx_tokens')} ({sys_tokens} sys + {total_tokens - sys_tokens} chat)")

    fluxlite_md = extra.get("fluxlite_md", "")
    if fluxlite_md:
        md_len = len(fluxlite_md)
        md_tokens = estimate_tokens(fluxlite_md)
        console.print(f"    {_('project_ctx')}: FLUXLITE.md ({md_len} {_('ctx_chars')}, ~{md_tokens} {_('ctx_tokens')})")
    else:
        console.print(f"    {_('project_ctx')}: [{GRAY}]{_('ctx_no_project')}[/]")

    instructions = extra.get("instructions_md", "")
    if instructions:
        ins_len = len(instructions)
        ins_tokens = estimate_tokens(instructions)
        console.print(f"    Instructions:  INSTRUCTIONS.md ({ins_len} {_('ctx_chars')}, ~{ins_tokens} {_('ctx_tokens')})")
    else:
        console.print(f"    Instructions:  [{GRAY}]{_('ctx_not_loaded')}[/]")

    project_map = extra.get("project_map", "")
    if project_map:
        pm_lines = project_map.count("\n") + 1
        console.print(f"    Project map:   {pm_lines} lines (symbols + sizes)")
    else:
        console.print(f"    Project map:   [{GRAY}]not generated[/]")

    git = extra.get("git_context", "")
    if git:
        lines = git.count("\n") + 1
        branch = extra.get("git_branch", "?")
        console.print(f"    {_('git_state')}:     branch: {branch} ({lines} lines)")
    else:
        console.print(f"    {_('git_state')}:     [{GRAY}]{_('ctx_no_git')}[/]")
    console.print()


def _handle_git():
    """Run git commands interactively."""
    import subprocess
    cmd = get_input(f"  git ")
    if not cmd.strip():
        return
    try:
        r = subprocess.run(
            ["git"] + shlex.split(cmd),
            capture_output=True, text=True, timeout=30,
        )
        if r.stdout:
            console.print(f"  [{DIM}]{r.stdout.rstrip()}[/]")
        if r.stderr:
            console.print(f"  [{ORANGE}]{r.stderr.rstrip()}[/]")
        if r.returncode != 0 and not r.stderr:
            console.print(f"  [{RED}]{_('git_exit_code')} {r.returncode}[/]")
    except FileNotFoundError:
        console.print(f"  [{RED}]{_('git_not_found')}[/]")
    except Exception as e:
        console.print(f"  [{RED}]{e}[/]")


def _handle_plan(task: str, messages: list):
    """Start a planning session for a multi-step task."""
    if not task:
        console.print(f"  [{ORANGE}]Usage: /plan <task description>[/]")
        console.print(f"  [{GRAY}]Example: /plan refactor the user module with tests[/]")
        return

    from .mcp_client import init_all
    init_all()

    console.print(f"\n  [{PURPLE}]╔══ Planning Mode ══╗[/]")
    console.print(f"  [{PURPLE}]Task:[/] {task}")
    console.print(f"  [{GRAY}]1. AI analyzes task and creates a numbered plan[/]")
    console.print(f"  [{GRAY}]2. Executes each step with verification[/]")
    console.print(f"  [{GRAY}]3. Uses batch_edit for atomic multi-file changes[/]")
    console.print(f"  [{PURPLE}]╚{'═'*20}╝[/]")

    plan_prompt = (
        f"You are now in PLAN AND EXECUTE mode. Task: {task}\n\n"
        "## Protocol\n"
        "1. Analyze the task and output a numbered plan with each step's objective.\n"
        "2. Execute each step one at a time.\n"
        "3. For multi-file changes, use batch_edit (NOT individual file_write/file_edit calls) — "
        "this applies all changes atomically (all succeed or all roll back).\n"
        "4. After each file change, verify syntax / run relevant tests.\n"
        "5. When all steps complete, summarize what was done.\n\n"
        "## Available for batch changes\n"
        "- batch_edit(edits): Apply multiple file edits atomically. Pass a JSON array of edits.\n"
        "- search_replace(pattern, replacement, glob): Cross-file text replacement with dry-run.\n\n"
        "Begin by outputting your plan."
    )
    messages.append({"role": "user", "content": f"/plan {task}\n\n{plan_prompt}"})
    console.print(f"  [{GREEN}]Plan started. AI will analyze, plan, and execute step by step.[/]")


def _handle_mcp():
    """Manage MCP servers with radio_select."""
    from .mcp_client import (
        load_config, save_config, init_all, stop_all,
        stop_server, get_server_names, get_tool_list,
    )

    actions = [
        ("list", "List connected servers & tools"),
        ("add", "Add a new MCP server"),
        ("remove", "Remove an MCP server"),
        ("restart", "Restart all MCP servers"),
    ]
    act = radio_select("MCP Manager", actions)
    if not act:
        return

    if act == "list":
        servers = get_server_names()
        tools = get_tool_list()
        if not servers:
            console.print(f"  [{GRAY}]No MCP servers running.[/]")
            console.print(f"  [{GRAY}]{_('mcp_config_hint')}[/]")
        else:
            console.print(f"\n  [{CYAN}]MCP Servers ({len(servers)})[/]")
            for s in servers:
                console.print(f"    [{GREEN}]●[/] {s}")
            if tools:
                console.print(f"\n  [{PURPLE}]Tools ({len(tools)})[/]")
                for t in tools:
                    n, d = t.get("name", "?"), t.get("description", "")[:60]
                    console.print(f"    [{GREEN}]{n}[/]  [{GRAY}]{d}[/]")
        console.print()

    elif act == "add":
        name = get_input(f"  {_('mcp_server_name_prompt')} ").strip()
        if not name:
            return
        cmd = get_input(f"  {_('mcp_command_prompt')} ").strip()
        if not cmd:
            return
        args_str = get_input(f"  Arguments (space-separated): ").strip()
        args = args_str.split() if args_str else []
        env_str = get_input(f"  Env vars (KEY=val, optional): ").strip()
        env = {}
        if env_str:
            for pair in env_str.split():
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    env[k] = v

        servers = load_config()
        servers.append({"name": name, "command": cmd, "args": args, "env": env})
        save_config(servers)
        err = init_all()
        console.print(f"  [{GREEN}]{_('mcp_added')} {name}[/]")
        if err:
            for e in err:
                console.print(f"  [{ORANGE}]{e}[/]")

    elif act == "remove":
        servers = load_config()
        if not servers:
            return
        items = [(str(i + 1), s.get("name", "?")) for i, s in enumerate(servers)]
        pick = radio_select("Remove MCP server", items)
        if not pick:
            return
        idx = int(pick) - 1
        name = servers.pop(idx).get("name", "")
        save_config(servers)
        stop_server(name)
        console.print(f"  [{GREEN}]{_('mcp_removed')} {name}[/]")

    elif act == "restart":
        stop_all()
        errs = init_all()
        if errs:
            for e in errs:
                console.print(f"  [{ORANGE}]{e}[/]")
        else:
            console.print(f"  [{GREEN}]{_('mcp_restarted')}[/]")


def _handle_search(keyword: str):
    """Search session history for keyword, present results with radio_select."""
    sessions_dir = Path.home() / ".fluxlite" / "history"
    if not sessions_dir.exists():
        console.print(f"  [{GRAY}]{_('session_no_saved')}[/]")
        return

    files = sorted(sessions_dir.glob("*.json"), reverse=True)
    matches = []
    items = []
    kw_lower = keyword.lower()

    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for msg in data:
            content = msg.get("content", "")
            if kw_lower in content.lower():
                ts = f.stem[:15] if len(f.stem) >= 15 else f.stem
                snippet = content.strip()[:80].replace("\n", " ")
                matches.append((data, f))
                items.append((str(len(matches)), f"{ts}  \"{snippet}\""))
                break  # one entry per file

    if not matches:
        console.print(f"  [{GRAY}]No sessions match \"{keyword}\"[/]")
        return

    console.print(f"  [{CYAN}]Found {len(matches)} session(s) matching \"{keyword}\"[/]")
    pick = radio_select(f"{_('session_search_title')} {keyword}", items)
    if not pick:
        return

    data, path = matches[int(pick) - 1]
    actions = [
        ("load", "Load this session"),
        ("delete", "Delete"),
    ]
    act = radio_select(f"Session: {path.stem[:20]} — {len(data)} msgs", actions)

    if act == "load":
        CommandState.session_load_requested = True
        CommandState.session_load_data = data
        console.print(f"  [{PURPLE}]{_('session_switching')}[/]")
    elif act == "delete":
        path.unlink()
        console.print(f"  [{GREEN}]{_('session_deleted')}[/]")


def _show_history(messages, context_extra):
    """Print current conversation history (user + assistant messages)."""
    from rich.markdown import Markdown
    from .styles import CYAN, GRAY

    agent_name = (context_extra or {}).get("agent_name", "FluxLite")
    user_msgs = [m for m in messages if m.get("role") in ("user", "assistant")]
    if not user_msgs:
        console.print(f"  [{GRAY}]{_('session_no_conversation')}[/]")
        return

    console.print(f"  [{GRAY}]── Conversation ({len(user_msgs)} msgs) ──[/]")
    for msg in user_msgs:
        role = msg["role"]
        content = msg.get("content", "")
        if role == "user":
            console.print(f"  [{GREEN}]>> {content[:200]}[/]")
        elif role == "assistant":
            if content:
                console.print(f"  [{CYAN}]{agent_name}:[/]")
                console.print(Markdown(content[:500], code_theme="monokai"))
    console.print(f"  [{GRAY}]{'─'*45}[/]")


def _handle_sessions():

    """浏览和管理历史会话（全屏弹出框 + 黑底主题）。"""
    sessions_dir = Path.home() / ".fluxlite" / "history"
    if not sessions_dir.exists():
        console.print(f"  [{GRAY}]{_('session_no_saved')}[/]")
        return

    files = sorted(sessions_dir.glob("*.json"))
    if not files:
        console.print(f"  [{GRAY}]{_('session_no_saved')}[/]")
        return

    # 构建会话列表 + 缓存数据
    sessions_cache = {}
    items = []
    for i, f in enumerate(files, 1):
        key = str(i)
        try:
            data = json.loads(f.read_text())
            sessions_cache[key] = (data, f)
            count = len(data)
        except Exception:
            sessions_cache[key] = ([], f)
            count = 0
        ts = f.stem
        if len(ts) == 15:
            dt = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}  {ts[9:11]}:{ts[11:13]}"
        else:
            dt = ts
        items.append((key, f"{dt}  ({count} msgs)"))

    pick = radio_select("Sessions", items)
    if not pick:
        return

    data, path = sessions_cache.get(pick, ([], None))
    if path is None:
        return

    actions = [
        ("load", "Load this session"),
        ("delete", "Delete"),
    ]

    act = radio_select(f"Session: {path.stem[:20]} — {len(data)} msgs", actions)

    if act == "load":
        CommandState.session_load_requested = True
        CommandState.session_load_data = data
        console.print(f"  [{PURPLE}]{_('session_switching')}[/]")
    elif act == "delete":
        path.unlink()
        console.print(f"  [{GREEN}]{_('session_deleted')}[/]")
