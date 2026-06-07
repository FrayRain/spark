_LANG = "zh"

_STRINGS = {
    "zh": {
        # --- existing ---
        "welcome": "欢迎使用 FluxLite",
        "tool_running": "正在执行: {name}",
        "tool_result": "工具执行结果",
        "error": "错误",
        "no_api_key": "未配置 API Key，请编辑 ~/.fluxlite/config.toml 进行设置",
        "no_tavily_key": "未配置 Tavily API Key，搜索功能将无法使用",
        "config_created": "配置文件已创建: {path}",
        "exit": "再见",
        "thinking": "思考中",
        "responding": "响应中",
        "processing": "处理中",
        "show_memory": "查看身份信息、记忆与规则",
        "truncated": "回答已被截断",
        "compact_done": "记忆压缩完成（{count} 条目已合并）",
        "think_on": "推理模式已启用",
        "think_off": "推理模式已禁用",
        "think_display_on": "推理过程将持续显示",
        "think_display_off": "推理过程将自动收起",
        "think_effort_set": "推理难度已设为: {level}",
        "think_effort_current": "当前推理难度: {level}",
        "think_effort_low": "低",
        "think_effort_medium": "中",
        "think_effort_high": "高",
        "think_status": "推理: {mode}, 难度: {effort}",
        "help_desc": "显示此帮助信息",
        "clear_desc": "清除屏幕",
        "model_desc": "切换 AI 模型",
        "think_desc": "管理推理模式 on/off/effort/display",
        "compact_desc": "压缩记忆条目",
        "truncate_desc": "移除最近一条 AI 回答",
        "rule_desc": "添加一项注意事项",
        "tools_desc": "列出可用工具",
        "lang_desc": "切换语言 (zh/en)",
        "exit_desc": "退出程序",
        "new_desc": "新建会话（保存当前并开始新对话）",
        "sessions_desc": "浏览和管理历史会话",
        "toolresult_desc": "显示/隐藏工具返回值 on/off",
        "export_desc": "导出对话记录",
        "token_desc": "切换 Token 用量显示",
        "context_desc": "显示当前上下文状态（模型、消息数、token 估算等）",
        "rewind_desc": "撤销最近一轮对话（移除最后一条用户消息及其回答）",
        "rewind_done": "已撤销最近一轮对话",
        "truncate_smart": "已截断最早的工具调用轮次",
        "truncate_exchange": "已截断最早的一轮对话",
        "context_title": "上下文信息",
        "msg_count": "消息数",
        "system_size": "系统提示",
        "project_ctx": "项目上下文",
        "git_state": "Git 状态",
        "token_estimate": "Token 估算",
        "cumulative": "累计",
        "hooks_desc": "列出 ~/.fluxlite/hooks/ 中的钩子脚本",
        "sandbox_desc": "管理沙箱模式 (on/off/review/apply/discard/status)",
        "plan_desc": "计划和执行多步任务，使用 batch_edit 进行原子化批量修改",
        "knowledge_desc": "构建和搜索项目代码的本地知识库",
        "summarize_desc": "用 AI 总结当前对话并保存为记忆，下次新会话自动加载",
        "summarize_done": "对话总结已保存为记忆",

        # --- identity ---
        "identity_title": "身份设置 (首次设置身份)",
        "identity_intro": "让我们互相认识一下！",
        "identity_ask_name": "我该怎么称呼你？",
        "identity_ask_ai_name": "你想给我起什么名字？",
        "identity_ask_personality": "描述我的性格（可选）",

        # --- compress ---
        "compress_warning": "上下文 {total}/{max_tok} — 自动裁剪旧工具轮次",
        "compress_critical": "上下文紧张 {total}/{max_tok} — 移除最早的一轮对话",
        "compress_summarized": "已智能压缩早期对话（{n} 条消息 → 摘要）",
        "compress_label": "摘要",

        # --- confirm tool ---
        "confirm_code_exec": "代码执行 ({lang})",
        "confirm_allow_title": "允许 {name}？",
        "confirm_allow_once": "允许一次",
        "confirm_skip": "跳过此次调用",
        "confirm_deny": "拒绝",
        "confirm_allow_all": "本次会话始终允许 {name}",
        "confirm_cancelled": "[已取消] 操作已被用户取消",
        "confirm_cancel_status": "{name} 已取消",

        # --- interrupt / retry ---
        "interrupt_edit": "给出反馈并继续",
        "interrupt_restart": "从头重新生成",
        "interrupt_accept": "接受部分回答",
        "interrupt_rewind": "丢弃并回退",
        "interrupt_title": "中断",
        "interrupt_partial": "--- 部分输出 ---",
        "interrupt_more_chars": "...（还有 {n} 个字符）",
        "interrupt_guidance": "你的建议：",
        "interrupt_annotation": "[用户中断]",
        "interrupt_no_retries": "无剩余重试次数，接受部分输出",
        "interrupt_accepted": "已接受部分回答",
        "interrupt_rewinding": "回退中...",
        "retry_cleanup": "已清理孤立工具消息，重试中...",
        "retry_attempt": "第 {n}/{max} 次重试...",
        "retry_error": "！{e}",
        "retry_final_error": "× {e}",

        # --- startup ---
        "startup_plugins": "已加载 {count} 个插件",
        "startup_mcp_error": "MCP: {e}",
        "startup_session_loaded": "已加载会话（{count} 条消息）— /last 查看",
        "startup_info_bar": "模型: {model}     /help  /tools  /memory  /exit",
        "startup_timing": "启动耗时: {elapsed:.1f}s",

        # --- main loop ---
        "main_exit_confirm": "退出？(y/N)",
        "main_new_session": "已创建新会话",
        "main_session_loaded": "已加载会话",
        "main_rewound": "！已撤销最近一轮对话",
        "main_empty_response": "AI 返回了空回答",
        "main_context_warning": "上下文 ~{total}/{max_tok} — 建议 /truncate 或 /rewind",
        "main_plan_progress": "━ 计划: {goal}  {bar}  {done}/{total}",
        "main_max_turns": "已达到最大轮次",
        "main_git_commit_msg": "fluxlite: AI 自动提交 {date}",
        "main_git_commit_ok": "✓ {short}",
        "main_git_preview": "将提交以下变更:",
        "main_git_confirm": "提交这些变更？(Y/n) [Y=提交]",
        "main_git_aborted": "已取消提交",

        # --- tool group display ---
        "toolgroup_quality_issue": "质量门问题",
        "toolgroup_auto_fix_prompt": "自动修复 {name}？",
        "toolgroup_fix_option": "用 AI 修复",
        "toolgroup_skip_option": "跳过（AI 将看到错误）",
        "toolgroup_fix_failed": "修复失败: {detail}",
        "toolgroup_fix_ok": "✓ 文件已修复",
        "toolgroup_fix_skipped": "自动修复已跳过（LLM 错误）",

        # --- memory ---
        "memory_name": "名字:",
        "memory_user": "用户:",
        "memory_personality": "性格:",
        "memory_no_rules": "没有规则",
        "memory_summarizing": "正在总结对话...",
        "memory_summary_saved": "总结已保存到记忆",
        "memory_too_few": "消息太少，无法总结",
        "memory_already_compact": "记忆已经是紧凑状态（{count} 条）",
        "memory_recorded": "记忆已记录: {content}",
        "memory_recent": "最近的记忆:\n{result}",

        # --- command help descriptions (missing 14) ---
        "git_desc": "交互式运行 Git 命令",
        "autocommit_desc": "切换 AI 文件修改后自动提交",
        "autodebug_desc": "切换代码执行失败时自动调试",
        "search_desc": "按关键词搜索历史会话",
        "mcp_desc": "管理 MCP 服务器 (添加/删除/列表)",
        "hooks_cmd_desc": "列出 ~/.fluxlite/hooks/ 中的钩子脚本",
        "plugin_desc": "管理插件 (list/info/enable/disable/create/reload)",
        "sandbox_cmd_desc": "管理沙箱 (on/off/review/apply/discard/status)",
        "last_desc": "显示当前对话历史",
        "init_desc": "为此项目生成 FLUXLITE.md",
        "diff_desc": "查看未提交的变更",
        "review_desc": "AI 代码审查已暂存的变更",
        "fix_cmd_desc": "自动修复上一次 lint/test 错误",
        "pin_desc": "固定文件以防止被截断",
        "plan_cmd_desc": "计划和执行多步任务，使用 batch_edit 进行原子化修改",

        # --- command feedback ---
        "cmd_available_models": "可用模型",
        "cmd_select_model": "选择模型:",
        "cmd_model_name": "模型名称:",
        "cmd_model_label": "模型:",
        "cmd_tools_header": "工具 ({count})",
        "cmd_nothing_truncate": "没有可截断的内容",
        "cmd_rule_recorded": "规则已记录:",
        "cmd_toolresult_on": "工具结果显示: 开",
        "cmd_toolresult_off": "工具结果显示: 关",
        "cmd_token_display": "Token 用量显示:",
        "cmd_autocommit_status": "Git 自动提交:",
        "cmd_export_header": "# FluxLite 对话导出\n\n",
        "cmd_export_to": "已导出到:",
        "cmd_export_failed": "导出失败:",
        "cmd_unknown": "未知命令",
        "cmd_did_you_mean": "你要找的是不是",
        "cmd_lang_prompt": "语言 (1=zh, 2=en):",
        "cmd_search_keyword": "搜索关键词:",

        # --- context display ---
        "ctx_no_project": "FLUXLITE.md 未加载",
        "ctx_not_loaded": "未加载",
        "ctx_no_git": "无 Git 仓库",
        "ctx_chars": "字符",
        "ctx_tokens": "token",

        # --- git ops ---
        "git_not_found": "未找到 git",
        "git_exit_code": "退出码:",
        "git_no_changes": "无变更",
        "git_no_commits": "无提交记录",

        # --- sandbox ---
        "sandbox_usage": "用法: /sandbox <on|off|review|apply|discard|status>",
        "sandbox_enabled": "沙箱: 已启用（临时目录: {path}）",
        "sandbox_disabled": "沙箱: 已禁用",
        "sandbox_no_changes": "无待处理的变更",
        "sandbox_not_active": "沙箱未激活",
        "sandbox_applied": "已将 {count} 个文件从沙箱同步到项目",
        "sandbox_discard_ok": "沙箱已丢弃（已创建新的空沙箱）",
        "sandbox_status_disabled": "沙箱: 已禁用",
        "sandbox_status_enabled": "沙箱: 已启用  文件: {count}  目录: {dir}",

        # --- hooks ---
        "hook_timed_out": "[hook] {name} 超时 ({timeout}s)",
        "hook_error": "[hook] {name} 错误: {e}",
        "hook_no_dir": "无钩子目录 (~/.fluxlite/hooks/)",
        "hook_no_scripts": "在 ~/.fluxlite/hooks/ 中未找到钩子脚本",
        "hook_not_found": "钩子 '{name}' 未找到",

        # --- file ops ---
        "file_write_ok": "已写入 {len} 个字符到 {path}",
        "file_write_failed": "写入失败: {e}",
        "file_read_failed": "读取失败: {e}",
        "file_not_found": "找不到文件: {path}",
        "file_edit_ok": "已在 {path} 替换 1 处",
        "file_edit_not_found": "在 {path} 中未找到 old_string",
        "file_append_ok": "已在 {path} 追加 {len} 个字符",
        "file_append_failed": "追加失败: {e}",
        "file_delete_ok": "已删除 {path}",
        "file_delete_failed": "删除失败: {e}",
        "file_access_denied": "拒绝访问: {path} 是系统目录",

        # --- code exec ---
        "exec_lint_ok": "[lint] OK",
        "exec_blocked": "[error] 已拦截: 检测到潜在的破坏性命令",
        "exec_syntax_error": "[error] 语法错误: {e}",
        "exec_timed_out": "[error] 执行超时 ({timeout}s)",
        "exec_error": "[error] 执行错误: {e}",
        "exec_exit_code": "[error] 退出码: {code}",
        "exec_no_output": "[output]（无输出）",
        "exec_unsupported_lang": "[error] 不支持的语言: {lang}（使用 python, bash 或 shell）",
        "exec_output_truncated": "...（还有 {n} 行）",

        # --- planner ---
        "plan_no_goal": "请提供计划目标。",
        "plan_no_steps": "请提供计划的步骤，每行一个。例如：\n1. 创建项目结构\n2. 实现核心逻辑\n3. 编写测试",
        "plan_header": "=== 计划: {id} ===",
        "plan_goal": "目标: {goal}",
        "plan_progress": "进度: {bar}",
        "plan_steps": "步骤:",
        "plan_footer": "完成后调用 self_review 验证结果。",
        "plan_no_id": "请提供 task_planner 返回的 plan_id。",
        "plan_review_header": "=== 自我审查 ===",
        "plan_not_found": "（在工作记忆中未找到计划 {id}）",
        "plan_review_result": "结果:",
        "plan_checklist_1": "结果是否符合原始目标？",
        "plan_checklist_2": "是否处理了所有边界情况？",
        "plan_checklist_3": "代码/测试质量是否可接受？",
        "plan_checklist_4": "是否引入了任何回归？",
        "plan_checklist_5": "是否有遗漏？",
        "plan_review_footer": "回复 Pass 或标记特定项目为 Fail 以触发返工。",

        # --- batch edit ---
        "batch_invalid_json": "[batch_edit] 无效的 JSON: {e}",
        "batch_all_ok": "[batch_edit] 所有编辑已成功应用",
        "batch_failed": "[batch_edit] 失败: {e}\n  变更已回滚。",
        "batch_rollback_warning": "\n  警告: 部分回滚！",

        # --- refactor ---
        "refactor_missing_params": "[refactor_rename] 需要 old_name 和 new_name",
        "refactor_no_matches": "[refactor_rename] 未找到包含 {name} 的文件",
        "refactor_dry_run": "\n  使用 dry_run=False 来应用更改",

        # --- search_replace ---
        "srch_no_matches": "[search_replace] 未找到包含 {pattern} 的文件",
        "srch_write_failed": "[search_replace] 写入失败: {e}",
        "srch_dry_run": "\n  使用 dry_run=False 来应用更改",

        # --- code search ---
        "codesrch_no_matches": "未找到匹配 {pattern} 的结果",
        "codesrch_truncated": "\n...（还有 {n} 个匹配结果）",

        # --- test runner ---
        "test_timed_out": "[error] 测试超时 ({timeout}s)",
        "test_failed": "[error] 测试失败，退出码 {code}",
        "test_no_output": "[output]（无输出）",

        # --- subagent ---
        "subagent_llm_error": "[subagent] LLM 错误: {e}",
        "subagent_max_turns": "[subagent] 已达到最大轮次",
        "subagent_invalid_json": "[error] 无效的 tasks JSON: {e}",
        "subagent_not_array": "[error] tasks 必须是 JSON 数组",
        "subagent_timeout": "[subagent] 超时",
        "subagent_result_header": "=== 代理 {i}: {label} ===",
        "subagent_truncated": "...（已截断）",

        # --- network ---
        "http_no_url": "错误: 需要 url",
        "http_timeout": "错误: 请求超时 ({timeout}s)",
        "http_connection_error": "错误: 连接失败: {e}",
        "http_error": "错误: {e}",
        "http_download_ok": "已下载 {size}（{bytes} 字节）到 {path}",
        "http_scrape_no_text": "（未提取到可读文本）",

        # --- browser ---
        "browser_closed": "浏览器已关闭",
        "browser_no_url": "错误: 需要 url",
        "browser_navigated": "已导航到 {url}\n标题: {title}",
        "browser_clicked": "已点击 {selector}",
        "browser_filled": "已填写 {selector}: '{text}'",
        "browser_screenshot_ok": "截图已保存到 {path}",
        "browser_unknown_action": "未知操作: {action}。支持: open, click, fill, html, text, title, evaluate, screenshot, close",
        "browser_error": "浏览器错误 ({action}): {err}",

        # --- knowledge ---
        "know_not_init": "[knowledge] 知识库未初始化",
        "know_build_failed": "[knowledge] 构建失败: {e}",
        "know_no_matches": "[knowledge] 未找到匹配结果",
        "know_up_to_date": "[knowledge] 索引已是最新（{chunks} 块, {elapsed:.1f}s）",
        "know_no_files": "[knowledge] 未找到可索引的文件",
        "know_indexed": "[knowledge] 已索引 {chunks} 个块（来自 {files} 个文件, mode={mode}, {elapsed:.1f}s）",
        "know_building": "正在构建知识索引...",
        "know_not_built": "知识库尚未构建。使用 /knowledge build",
        "know_usage": "用法: /knowledge <build|status|search>",

        # --- plugin ---
        "plugin_no_plugins": "在 ~/.fluxlite/plugins/ 中未找到插件",
        "plugin_not_found": "未找到插件 '{name}'",
        "plugin_enabled_ok": "插件 '{name}' 已启用",
        "plugin_disabled_ok": "插件 '{name}' 已禁用",
        "plugin_reloaded": "插件已重载",
        "plugin_already_exists": "插件 '{name}' 已存在于 {dir}",
        "plugin_invalid_name": "无效的插件名 '{name}' — 仅允许字母、数字和下划线",

        # --- MCP ---
        "mcp_no_servers": "未连接 MCP 服务器。\n在 ~/.fluxlite/mcp.json 中配置或使用 /mcp 管理。",
        "mcp_config_hint": "在 ~/.fluxlite/mcp.json 中配置",
        "mcp_added": "已添加:",
        "mcp_removed": "已移除:",
        "mcp_restarted": "MCP 服务器已重启",
        "mcp_invalid_json": "[mcp] 无效的 JSON 参数: {e}",
        "mcp_server_name_prompt": "服务器名称:",
        "mcp_command_prompt": "命令 (例如 node, python):",

        # --- sessions ---
        "session_no_saved": "无保存的会话",
        "session_switching": "正在切换会话...",
        "session_deleted": "会话已删除",
        "session_no_conversation": "暂无对话",
        "session_search_title": "搜索:",

        # --- project map / context generation ---
        "proj_fluxlite_exists": "FLUXLITE.md 已存在。是否覆盖？",
        "proj_overwrite": "覆盖",
        "proj_cancel": "取消",
        "proj_generated_ok": "FLUXLITE.md 已生成（{len} 个字符）",
        "proj_write_failed": "写入 FLUXLITE.md 失败",
        "proj_restart_hint": "重启 FluxLite 以加载项目上下文。",

        # --- auto-debug ---
        "auto_debug_on": "自动调试: 开",
        "auto_debug_off": "自动调试: 关",
        "auto_debug_analysis": "\n[auto-debug] {analysis}",
        "auto_debug_failed": "\n[auto-debug] 分析失败",

        # --- various ---
        "user_label": "你",
        "search_no_title": "无标题",
        "auto_test_prefix": "\n\n[自动测试]\n{result}",

        # --- wizard ---
        "api_provider": "API 服务商",
        "api_key_setup": "API 密钥",
        "test_connection": "测试连接",
        "saving": "保存配置",

        # --- terminal ---
        "terminal_session_terminated": "[会话已终止]",
        "terminal_write_error": "[写入错误: {e}]",
        "terminal_timeout": "[超时]",

        # --- registry ---
        "tool_unknown": "{icon} 未知工具: {name}",
        "tool_perm_error": "{icon} {e}",
        "tool_exec_error": "{icon} {name} 执行错误: {e}",
        "tool_retry_recovered": "\n  [已重试 {n} 次，已恢复]",
        "tool_retry_giving_up": "\n  [已重试 {n} 次，放弃]",
        "sandbox_unknown_action": "[sandbox] 未知操作: {action}（使用 on/off/review/apply/discard/status）",
        "rule_no_rules": "没有规则。",
        "rule_removed": "已移除规则: {content}",
        "rule_remove_error": "错误: 索引 {index} 无对应规则",
        "memory_none": "无记忆记录",
        "config_updated": "配置已更新: {key} = {value}",
        "know_results_header": "[knowledge] 前 {n} 个结果: {query}",
        "mcp_no_tools": "MCP 服务器: {servers}\n（无工具声明）",
        "mcp_tools_summary": "MCP: {servers} 个服务器共 {tools} 个工具",

        # --- knowledge.py ---
        "memory_summary_label": "会话总结",
        "memory_summary_prompt_en": "将以下对话总结为 3-5 个要点。捕获：用户偏好、决策、关键事实、项目上下文。\n\n{content}",
        "memory_summary_prompt_zh": "将以下对话总结为 3-5 个要点（中文）。捕获：用户偏好、决策、关键事实、项目上下文。\n\n{content}",

        # --- system_tools.py ---
        "list_processes_desc": "查看系统正在运行的进程（PID、内存、名称），支持排序和名称过滤",
        "launch_app_desc": "打开应用程序、文件、目录或 URL（自动识别系统类型调用默认程序）",
        "sys_launched": "[system] 已启动 {target}（PID {pid}）",
        "sys_opened": "[system] 已打开 {target}",
        "sys_not_found": "[system] 未找到: {target}",
        "sys_launch_error": "[system] 打开失败 {target}: {error}",

        # --- auto mode ---
        "auto_tool_done": "[tool] {name} 完成",
        "auto_tool_running": "[tool] {name}",
        "auto_tool_calls": "[tool calls: {names} — 使用 --auto 执行]",

        # --- token display ---
        "token_in": "入: {value}  ",
        "token_out": "出: {value}  ",

        # --- commands: memory ---
        "memory_rules_header": "规则 ({n})",
        "memory_memories_header": "记忆 ({n})",

        # --- commands: lang ---
        "lang_set_zh": "lang: zh",
        "lang_set_en": "lang: en",

        # --- commands: think ---
        "think_effort_usage": "/think effort <low|medium|high>",

        # --- commands: knowledge ---
        "know_search_prompt": "搜索:",
        "know_no_matches_for": "无匹配结果",
        "know_results_count": "━ 结果 ({n})",

        # --- commands: plugin ---
        "plugin_usage": "用法: /plugin <list|info|enable|disable|create|reload>",

        # --- commands: context display ---
        "ctx_model_label": "模型:",
        "ctx_instructions_label": "说明:",
        "ctx_project_map_label": "项目地图:",
        "ctx_branch_label": "分支:",
        "ctx_lines_suffix": "行",
        "ctx_not_generated": "未生成",
        "ctx_no_system_prompt": "无系统提示",

        # --- commands: pin ---
        "pin_unpinned": "已取消固定: {f}",
        "pin_pinned": "已固定: {f}",
        "pin_pinned_files": "已固定的文件:",
        "pin_no_files": "无固定文件",

        # --- commands: diff ---
        "diff_header": "━━━ git diff ━━━",

        # --- commands: review ---
        "review_no_changes": "无变更可审查",
        "review_requested": "已请求审查（{len} 字符 diff）",

        # --- commands: fix ---
        "fix_no_error": "对话中未发现错误",
        "fix_request_sent": "已发送分析请求",

        # --- commands: rewind ---
        "rewind_nothing": "无操作可撤销",

        # --- commands: git ---
        "git_prompt": "git ",

        # --- commands: plan ---
        "plan_usage": "用法: /plan <任务描述>",
        "plan_usage_example": "示例: /plan 重构 user 模块并编写测试",
        "plan_header_mode": "╔══ 计划模式 ══╗",
        "plan_task_label": "任务:",
        "plan_step_1": "1. AI 分析任务并创建编号计划",
        "plan_step_2": "2. 逐步执行并验证",
        "plan_step_3": "3. 使用 batch_edit 进行原子化批量修改",
        "plan_started": "计划已启动。AI 将分析、计划并逐步执行。",

        # --- commands: mcp ---
        "mcp_action_list": "列出已连接的服务器和工具",
        "mcp_action_add": "添加新的 MCP 服务器",
        "mcp_action_remove": "移除 MCP 服务器",
        "mcp_action_restart": "重启所有 MCP 服务器",
        "mcp_manager_title": "MCP 管理器",
        "mcp_servers_header": "MCP 服务器 ({n})",
        "mcp_tools_header": "工具 ({n})",
        "mcp_add_args": "参数（空格分隔）:",
        "mcp_add_env": "环境变量（KEY=val，可选）:",
        "mcp_remove_title": "移除 MCP 服务器",

        # --- commands: search / history / session ---
        "search_no_matches_for": "搜索 \"{kw}\" 无匹配会话",
        "search_found_matches": "找到 {n} 个匹配 \"{kw}\" 的会话",
        "search_action_load": "加载此会话",
        "search_action_delete": "删除",
        "search_session_label": "会话: {name} — {n} 条消息",
        "history_conversation_header": "── 对话 ({n} 条消息) ──",
        "session_list_title": "会话列表",

        # --- commands: export ---
        "export_user_header": "## 用户",
        "export_assistant_header": "## 助手",
        "export_tool_result_prefix": "> 工具结果:",

        # --- commands: model ---
        "cmd_custom_input": "[自定义] 手动输入",
    },
    "en": {
        # --- existing ---
        "welcome": "Welcome to FluxLite",
        "tool_running": "Running tool: {name}",
        "tool_result": "Tool result",
        "error": "Error",
        "no_api_key": "No API Key configured. Edit ~/.fluxlite/config.toml to set it",
        "no_tavily_key": "No Tavily API Key configured. Search will be unavailable",
        "config_created": "Config created: {path}",
        "exit": "Goodbye",
        "thinking": "Thinking",
        "responding": "Responding",
        "processing": "Processing",
        "show_memory": "View identity, memory and rules",
        "truncated": "Response truncated",
        "compact_done": "Memory compaction complete ({count} entries compacted)",
        "think_on": "Reasoning enabled",
        "think_off": "Reasoning disabled",
        "think_display_on": "Reasoning display: persistent",
        "think_display_off": "Reasoning display: collapsed",
        "think_effort_set": "Reasoning effort set to: {level}",
        "think_effort_current": "Reasoning effort: {level}",
        "think_effort_low": "low",
        "think_effort_medium": "medium",
        "think_effort_high": "high",
        "think_status": "Thinking: {mode}, Effort: {effort}",
        "help_desc": "Display this help information",
        "clear_desc": "Clear the screen",
        "model_desc": "Switch AI model",
        "think_desc": "Manage reasoning on/off/effort/display",
        "compact_desc": "Compact memory entries",
        "truncate_desc": "Remove the most recent AI response",
        "rule_desc": "Add a user rule",
        "tools_desc": "List available tools",
        "lang_desc": "Switch language (zh/en)",
        "exit_desc": "Exit the program",
        "new_desc": "Start a new session (saves current conversation)",
        "sessions_desc": "Browse and manage session history",
        "toolresult_desc": "Toggle tool result display on/off",
        "export_desc": "Export conversation",
        "token_desc": "Toggle token usage display",
        "context_desc": "Show current context state (model, message count, token estimates, etc.)",
        "rewind_desc": "Undo the last exchange (remove last user message and its response)",
        "rewind_done": "Rewound last exchange",
        "truncate_smart": "Truncated oldest tool call cycle",
        "truncate_exchange": "Truncated oldest exchange",
        "context_title": "Context Info",
        "msg_count": "Messages",
        "system_size": "System prompt",
        "project_ctx": "Project context",
        "git_state": "Git state",
        "token_estimate": "Token estimate",
        "cumulative": "Cumulative",
        "hooks_desc": "List hook scripts in ~/.fluxlite/hooks/",
        "sandbox_desc": "Manage sandbox mode (on/off/review/apply/discard/status)",
        "plan_desc": "Plan and execute multi-step tasks with batch_edit for atomic changes",
        "knowledge_desc": "Build and search a local knowledge base indexed from project code",
        "summarize_desc": "AI-summarize the current conversation and save as memory for future sessions",
        "summarize_done": "Conversation summary saved to memory",

        # --- tool descriptions (existing) ---
        "写入文件（如果存在则覆盖）": "Write a file (overwrite if exists)",
        "读取文件内容": "Read file contents",
        "精确替换文件中的某段文本": "Replace exact text in a file",
        "在文件末尾追加内容": "Append content to end of a file",
        "删除文件": "Delete a file",
        "列出目录内容（支持 glob 模式过滤）": "List directory contents (supports glob pattern filtering)",
        "执行 Python/Bash/Shell 代码或任意命令（npm, cargo, go, curl 等），返回 stdout/stderr": "Execute Python/Bash/Shell code or any command (npm, cargo, go, curl, etc.), returns stdout/stderr",
        "联网搜索当前信息": "Search the web for current information",
        "记录一条记忆，用于保存重要信息备后续查阅": "Record a memory for important information to reference later",
        "查阅已保存的记忆": "View saved memories",
        "添加一条行为规则（当用户明确要求记住某条规则，或反复强调同一行为模式时使用）": "Add a behavior rule (use when the user explicitly asks to remember a rule or repeatedly emphasizes a behavior pattern)",
        "移除一条行为规则（通过 /memory 可查看当前规则列表）": "Remove a behavior rule (view current rules with /memory)",
        "查看 Git 工作区状态（分支名、未提交的变更）": "View Git working tree status (branch name, uncommitted changes)",
        "查看未提交的代码差异（可指定文件或查看已缓存的变更）": "View uncommitted code diff (optionally by file or staged changes)",
        "查看最近的提交历史": "View recent commit history",
        "缓存文件变更（默认缓存全部变更）": "Stage file changes (defaults to all changes)",
        "提交已缓存的变更到本地仓库（默认自动缓存所有变更）": "Commit staged changes to local repository (default auto-stages all changes)",
        "在项目代码中搜索匹配正则表达式的文件内容（支持路径过滤和文件类型过滤）": "Search file contents matching a regex pattern in project code (supports path and file type filters)",
        "使用 glob 模式查找文件和目录（支持 **/ 递归匹配）": "Find files and directories using glob patterns (supports **/ recursive matching)",
        "运行测试命令并返回结构化输出（解析 pytest/unittest 结果）": "Run a test command and return structured output (parses pytest/unittest results)",
        "调用 MCP 服务器上的工具（如连接数据库、操作 GitHub 等）。先用 mcp_list 查看可用工具": "Call a tool on an MCP server (e.g. connect database, operate GitHub). Use mcp_list first to see available tools",
        "列出所有已连接的 MCP 服务器及其提供的工具": "List all connected MCP servers and their tools",
        "修改 FluxLite 自身设置（语言、安全模式、超时等）": "Modify FluxLite settings (language, safe mode, timeout, etc.)",
        "查看当前所有行为规则": "View all current behavior rules",
        "手动触发 hook 脚本（如 pre_all、post_file_write、或具体脚本名）": "Manually trigger a hook script (e.g. pre_all, post_file_write, or specific script name)",
        "列出 ~/.fluxlite/hooks/ 下所有已发现的 hook 脚本": "List all discovered hook scripts in ~/.fluxlite/hooks/",
        "并行启动多个子 AI 代理，各自独立完成子任务。每个代理有独立的 LLM 和工具。tasks 是 JSON 数组": "Spawn multiple parallel sub-agents, each independently completing a task. Each has its own LLM and tools. tasks is a JSON array",
        "管理一个持久终端会话，支持连续执行多条命令并保留环境状态。action=start 创建新会话，action=run 执行命令，action=stop 关闭会话": "Manage a persistent terminal session for running multiple commands with preserved state. action=start creates session, action=run executes command, action=stop closes session",
        "创建一个结构化任务计划。先规划步骤再开始执行，减少返工。返回带步骤清单的计划 ID": "Create a structured task plan. Plan steps before executing to reduce rework. Returns plan ID with step checklist",
        "对照计划审查已完成的工作。传入 plan_id 和结果摘要，返回审查清单供确认": "Review completed work against a plan. Provide plan_id and result summary, returns review checklist for confirmation",
        "发送 HTTP 请求（GET/POST/PUT/DELETE/PATCH/HEAD），用于调用 API、测试接口、获取网页内容": "Send HTTP request (GET/POST/PUT/DELETE/PATCH/HEAD) for API calls, interface testing, or fetching web content",
        "从 URL 下载文件并保存到本地磁盘，支持大文件、自动推断文件名": "Download a file from URL and save to local disk, supports large files and auto-inferred filenames",
        "爬取网页内容，支持提取纯文本、HTML 源码、所有超链接，无需额外依赖": "Scrape web page content, supports extracting plain text, HTML source, or all hyperlinks. No extra dependencies required",
        "控制无头浏览器打开网页、点击、填表、截图、执行 JS。需要安装 Playwright (pip install playwright && playwright install chromium)": "Control a headless browser to open pages, click, fill forms, screenshot, and execute JS. Requires Playwright (pip install playwright && playwright install chromium)",

        # --- identity ---
        "identity_title": "Identity Setup",
        "identity_intro": "Let's get to know each other!",
        "identity_ask_name": "What should I call you?",
        "identity_ask_ai_name": "What would you like to name me?",
        "identity_ask_personality": "Describe my personality (optional)",

        # --- compress ---
        "compress_warning": "Context at {total}/{max_tok} - auto-trimming old tool cycles",
        "compress_critical": "Context critical {total}/{max_tok} - removing oldest exchange",
        "compress_summarized": "Compressed early conversation ({n} messages → summary)",
        "compress_label": "Summary",

        # --- confirm tool ---
        "confirm_code_exec": "code_executor ({lang})",
        "confirm_allow_title": "Allow {name}?",
        "confirm_allow_once": "Allow once",
        "confirm_skip": "Skip this call",
        "confirm_deny": "Deny",
        "confirm_allow_all": "Allow all {name} this session",
        "confirm_cancelled": "[cancelled] Operation cancelled by user",
        "confirm_cancel_status": "{name}  cancelled",

        # --- interrupt / retry ---
        "interrupt_edit": "Give feedback and continue",
        "interrupt_restart": "Restart from scratch",
        "interrupt_accept": "Accept partial response",
        "interrupt_rewind": "Discard and rewind",
        "interrupt_title": "Interrupted",
        "interrupt_partial": "--- partial output ---",
        "interrupt_more_chars": "... ({n} more chars)",
        "interrupt_guidance": "Your guidance:",
        "interrupt_annotation": "[interrupted by user]",
        "interrupt_no_retries": "No retries left, accepting partial",
        "interrupt_accepted": "Accepted partial response",
        "interrupt_rewinding": "Rewinding...",
        "retry_cleanup": "Cleaned up orphaned tool messages, retrying...",
        "retry_attempt": "Retry {n}/{max}...",
        "retry_error": "! {e}",
        "retry_final_error": "x {e}",

        # --- startup ---
        "startup_plugins": "Plugins: {count} loaded",
        "startup_mcp_error": "MCP: {e}",
        "startup_session_loaded": "Loaded session ({count} msgs) -- /last to view",
        "startup_info_bar": "model: {model}     /help  /tools  /memory  /exit",
        "startup_timing": "startup: {elapsed:.1f}s",

        # --- main loop ---
        "main_exit_confirm": "Exit? (y/N)",
        "main_new_session": "New session started",
        "main_session_loaded": "Session loaded",
        "main_rewound": "! Rewound last exchange",
        "main_empty_response": "AI returned empty response",
        "main_context_warning": "ctx ~{total}/{max_tok} - /truncate or /rewind advised",
        "main_plan_progress": "━ Plan: {goal}  {bar}  {done}/{total}",
        "main_max_turns": "Max turns reached",
        "main_git_commit_msg": "fluxlite: AI {date}",
        "main_git_commit_ok": "✓ {short}",
        "main_git_preview": "Changes to commit:",
        "main_git_confirm": "Commit these changes? (Y/n) [Y=commit]",
        "main_git_aborted": "Commit cancelled",

        # --- tool group display ---
        "toolgroup_quality_issue": "Quality issue",
        "toolgroup_auto_fix_prompt": "Auto-fix {name}?",
        "toolgroup_fix_option": "Fix with AI",
        "toolgroup_skip_option": "Skip (AI will see error)",
        "toolgroup_fix_failed": "Fix failed: {detail}",
        "toolgroup_fix_ok": "File fixed",
        "toolgroup_fix_skipped": "Auto-fix skipped (LLM error)",

        # --- memory ---
        "memory_name": "Name:",
        "memory_user": "User:",
        "memory_personality": "Personality:",
        "memory_no_rules": "No rules set",
        "memory_summarizing": "Summarizing conversation...",
        "memory_summary_saved": "Summary saved to memory",
        "memory_too_few": "Too few messages to summarize",
        "memory_already_compact": "Memory is already compact ({count} entries)",
        "memory_recorded": "Memory recorded: {content}",
        "memory_recent": "Recent memories:\n{result}",

        # --- command help descriptions (missing 14) ---
        "git_desc": "Run git commands interactively",
        "autocommit_desc": "Toggle git auto-commit after AI file changes",
        "autodebug_desc": "Toggle auto-debug on code execution failure",
        "search_desc": "Search session history by keyword",
        "mcp_desc": "Manage MCP servers (add/remove/list)",
        "hooks_cmd_desc": "List hook scripts in ~/.fluxlite/hooks/",
        "plugin_desc": "Manage plugins (list/info/enable/disable/create/reload)",
        "sandbox_cmd_desc": "Manage sandbox (on/off/review/apply/discard/status)",
        "last_desc": "Show current conversation history",
        "init_desc": "Generate FLUXLITE.md for this project",
        "diff_desc": "View uncommitted changes",
        "review_desc": "AI code review of staged changes",
        "fix_cmd_desc": "Auto-fix last lint/test error",
        "pin_desc": "Pin files to protect from truncation",
        "plan_cmd_desc": "Plan and execute multi-step tasks with atomic batch_edit support",

        # --- command feedback ---
        "cmd_available_models": "Available Models",
        "cmd_select_model": "Select model:",
        "cmd_model_name": "Model name:",
        "cmd_model_label": "model:",
        "cmd_tools_header": "Tools ({count})",
        "cmd_nothing_truncate": "Nothing to truncate",
        "cmd_rule_recorded": "Rule recorded:",
        "cmd_toolresult_on": "Tool result display: on",
        "cmd_toolresult_off": "Tool result display: off",
        "cmd_token_display": "Token usage display:",
        "cmd_autocommit_status": "Git auto-commit:",
        "cmd_export_header": "# FluxLite Conversation Export\n\n",
        "cmd_export_to": "Exported to:",
        "cmd_export_failed": "Export failed:",
        "cmd_unknown": "unknown",
        "cmd_did_you_mean": "did you mean",
        "cmd_lang_prompt": "lang (1=zh, 2=en):",
        "cmd_search_keyword": "Search keyword:",

        # --- context display ---
        "ctx_no_project": "FLUXLITE.md not loaded",
        "ctx_not_loaded": "not loaded",
        "ctx_no_git": "no git repo",
        "ctx_chars": "chars",
        "ctx_tokens": "tokens",

        # --- git ops ---
        "git_not_found": "git not found",
        "git_exit_code": "exit code:",
        "git_no_changes": "No changes.",
        "git_no_commits": "No commits.",

        # --- sandbox ---
        "sandbox_usage": "Usage: /sandbox <on|off|review|apply|discard|status>",
        "sandbox_enabled": "Sandbox: enabled (temp: {path})",
        "sandbox_disabled": "Sandbox: disabled",
        "sandbox_no_changes": "No pending changes",
        "sandbox_not_active": "Sandbox not active",
        "sandbox_applied": "Applied {count} file(s) from sandbox to project",
        "sandbox_discard_ok": "Sandbox discarded (fresh empty sandbox created)",
        "sandbox_status_disabled": "Sandbox: disabled",
        "sandbox_status_enabled": "Sandbox: enabled  files: {count}  dir: {dir}",

        # --- hooks ---
        "hook_timed_out": "[hook] {name} timed out after {timeout}s",
        "hook_error": "[hook] {name} error: {e}",
        "hook_no_dir": "No hooks directory (~/.fluxlite/hooks/)",
        "hook_no_scripts": "No hook scripts found in ~/.fluxlite/hooks/",
        "hook_not_found": "Hook '{name}' not found",

        # --- file ops ---
        "file_write_ok": "[file] Written {len} chars to {path}",
        "file_write_failed": "[file] Write failed: {e}",
        "file_read_failed": "[file] Read failed: {e}",
        "file_not_found": "[file] File not found: {path}",
        "file_edit_ok": "[file] Replaced 1 occurrence in {path}",
        "file_edit_not_found": "[file] old_string not found in {path}",
        "file_append_ok": "[file] Appended {len} chars to {path}",
        "file_append_failed": "[file] Append failed: {e}",
        "file_delete_ok": "[file] Deleted {path}",
        "file_delete_failed": "[file] Delete failed: {e}",
        "file_access_denied": "Access denied: {path} is a system directory",

        # --- code exec ---
        "exec_lint_ok": "[lint] OK",
        "exec_blocked": "[error] Blocked: potentially destructive command detected",
        "exec_syntax_error": "[error] Syntax error: {e}",
        "exec_timed_out": "[error] Execution timed out after {timeout}s",
        "exec_error": "[error] Execution error: {e}",
        "exec_exit_code": "[error] Exit code: {code}",
        "exec_no_output": "[output] (no output)",
        "exec_unsupported_lang": "[error] Unsupported language: {lang} (use python, bash, or shell)",
        "exec_output_truncated": "... ({n} more lines)",

        # --- planner ---
        "plan_no_goal": "Please provide a goal for the plan.",
        "plan_no_steps": "Please provide steps for the plan, one per line. Example:\n1. Create the project structure\n2. Implement the core logic\n3. Write tests",
        "plan_header": "=== Plan: {id} ===",
        "plan_goal": "Goal: {goal}",
        "plan_progress": "Progress: {bar}",
        "plan_steps": "Steps:",
        "plan_footer": "Call self_review when done to verify the result.",
        "plan_no_id": "Please provide the plan_id from task_planner.",
        "plan_review_header": "=== Self Review ===",
        "plan_not_found": "(Plan {id} not found in working memory)",
        "plan_review_result": "Result:",
        "plan_checklist_1": "Does the result match the original goal?",
        "plan_checklist_2": "Are all edge cases handled?",
        "plan_checklist_3": "Is the code/test quality acceptable?",
        "plan_checklist_4": "Any regressions introduced?",
        "plan_checklist_5": "Is there anything missed?",
        "plan_review_footer": "Reply with Pass or mark specific items as Fail to trigger rework.",

        # --- batch edit ---
        "batch_invalid_json": "[batch_edit] Invalid JSON: {e}",
        "batch_all_ok": "[batch_edit] All edits applied successfully",
        "batch_failed": "[batch_edit] Failed: {e}\n  Changes rolled back.",
        "batch_rollback_warning": "\n  WARNING: partial rollback!",

        # --- refactor ---
        "refactor_missing_params": "[refactor_rename] old_name and new_name are required",
        "refactor_no_matches": "[refactor_rename] No files contain symbol {name!r}",
        "refactor_dry_run": "\n  Use dry_run=False to apply changes",

        # --- search_replace ---
        "srch_no_matches": "[search_replace] No files contain {pattern!r}",
        "srch_write_failed": "[search_replace] WRITE FAILED: {e}",
        "srch_dry_run": "\n  Use dry_run=False to apply changes",

        # --- code search ---
        "codesrch_no_matches": "No matches for {pattern!r}",
        "codesrch_truncated": "\n... ({n} more matches)",

        # --- test runner ---
        "test_timed_out": "[error] Tests timed out after {timeout}s",
        "test_failed": "[error] Tests failed with exit code {code}",
        "test_no_output": "[output] (no output)",

        # --- subagent ---
        "subagent_llm_error": "[subagent] LLM error: {e}",
        "subagent_max_turns": "[subagent] Max turns reached",
        "subagent_invalid_json": "[error] Invalid tasks JSON: {e}",
        "subagent_not_array": "[error] tasks must be a JSON array",
        "subagent_timeout": "[subagent] TIMEOUT",
        "subagent_result_header": "=== Agent {i}: {label} ===",
        "subagent_truncated": "...(truncated)",

        # --- network ---
        "http_no_url": "Error: url is required",
        "http_timeout": "Error: request timed out after {timeout}s",
        "http_connection_error": "Error: connection failed: {e}",
        "http_error": "Error: {e}",
        "http_download_ok": "Downloaded {size} ({bytes} bytes) to {path}",
        "http_scrape_no_text": "(no readable text extracted)",

        # --- browser ---
        "browser_closed": "Browser closed",
        "browser_no_url": "Error: url is required",
        "browser_navigated": "Navigated to {url}\nTitle: {title}",
        "browser_clicked": "Clicked {selector}",
        "browser_filled": "Filled {selector} with '{text}'",
        "browser_screenshot_ok": "Screenshot saved to {path}",
        "browser_unknown_action": "Unknown action: {action}. Supported: open, click, fill, html, text, title, evaluate, screenshot, close",
        "browser_error": "Browser error ({action}): {err}",

        # --- knowledge ---
        "know_not_init": "[knowledge] No knowledge base initialized",
        "know_build_failed": "[knowledge] Build failed: {e}",
        "know_no_matches": "[knowledge] No matches found",
        "know_up_to_date": "[knowledge] Index up to date ({chunks} chunks, {elapsed:.1f}s)",
        "know_no_files": "[knowledge] No indexable files found",
        "know_indexed": "[knowledge] Indexed {chunks} chunks from {files} files (mode={mode}, {elapsed:.1f}s)",
        "know_building": "Building knowledge index...",
        "know_not_built": "Knowledge base not built. Use /knowledge build",
        "know_usage": "Usage: /knowledge <build|status|search>",

        # --- plugin ---
        "plugin_no_plugins": "No plugins found in ~/.fluxlite/plugins/",
        "plugin_not_found": "Plugin '{name}' not found",
        "plugin_enabled_ok": "Plugin '{name}' enabled",
        "plugin_disabled_ok": "Plugin '{name}' disabled",
        "plugin_reloaded": "Plugins reloaded",
        "plugin_already_exists": "Plugin '{name}' already exists at {dir}",
        "plugin_invalid_name": "Invalid plugin name: '{name}' -- use letters, digits, underscores only",

        # --- MCP ---
        "mcp_no_servers": "No MCP servers connected.\nConfigure in ~/.fluxlite/mcp.json or use /mcp to manage.",
        "mcp_config_hint": "Configure in ~/.fluxlite/mcp.json",
        "mcp_added": "Added:",
        "mcp_removed": "Removed:",
        "mcp_restarted": "MCP servers restarted",
        "mcp_invalid_json": "[mcp] Invalid JSON arguments: {e}",
        "mcp_server_name_prompt": "Server name:",
        "mcp_command_prompt": "Command (e.g. node, python):",

        # --- sessions ---
        "session_no_saved": "No saved sessions",
        "session_switching": "Switching session...",
        "session_deleted": "Session deleted",
        "session_no_conversation": "No conversation yet",
        "session_search_title": "Search:",

        # --- project map / context generation ---
        "proj_fluxlite_exists": "FLUXLITE.md already exists. Overwrite?",
        "proj_overwrite": "Overwrite",
        "proj_cancel": "Cancel",
        "proj_generated_ok": "FLUXLITE.md generated ({len} chars)",
        "proj_write_failed": "Failed to write FLUXLITE.md",
        "proj_restart_hint": "Restart FluxLite to load project context.",

        # --- auto-debug ---
        "auto_debug_on": "Auto-debug: on",
        "auto_debug_off": "Auto-debug: off",
        "auto_debug_analysis": "\n[auto-debug] {analysis}",
        "auto_debug_failed": "\n[auto-debug] Analysis failed",

        # --- various ---
        "user_label": "You",
        "search_no_title": "No title",
        "auto_test_prefix": "\n\n[auto-test]\n{result}",

        # --- wizard ---
        "api_provider": "API Provider",
        "api_key_setup": "API Key",
        "test_connection": "Test Connection",
        "saving": "Save Configuration",

        # --- terminal ---
        "terminal_session_terminated": "[session terminated]",
        "terminal_write_error": "[write error: {e}]",
        "terminal_timeout": "[Timeout]",

        # --- registry ---
        "tool_unknown": "{icon} Unknown tool: {name}",
        "tool_perm_error": "{icon} {e}",
        "tool_exec_error": "{icon} {name} execution error: {e}",
        "tool_retry_recovered": "\n  [retried {n}x, recovered]",
        "tool_retry_giving_up": "\n  [retried {n}x, giving up]",
        "sandbox_unknown_action": "[sandbox] Unknown action: {action} (use on/off/review/apply/discard/status)",
        "rule_no_rules": "No rules.",
        "rule_removed": "Rule removed: {content}",
        "rule_remove_error": "Error: no rule at index {index}",
        "memory_none": "No memories recorded.",
        "config_updated": "Config updated: {key} = {value}",
        "know_results_header": "[knowledge] Top {n} results for: {query}",
        "mcp_no_tools": "MCP servers: {servers}\n(no tools advertised)",
        "mcp_tools_summary": "MCP: {tools} tools across {servers} servers",

        # --- knowledge.py ---
        "memory_summary_label": "Session Summary",
        "memory_summary_prompt_en": "Summarize this conversation in 3-5 bullet points. Capture: user preferences, decisions, key facts, project context.\n\n{content}",
        "memory_summary_prompt_zh": "将以下对话总结为 3-5 个要点（中文）。捕获：用户偏好、决策、关键事实、项目上下文。\n\n{content}",

        # --- system_tools.py ---
        "list_processes_desc": "List running processes with PID, memory, and name. Supports sorting and filtering",
        "launch_app_desc": "Open an application, file, directory, or URL using the system default handler",
        "sys_launched": "[system] Launched {target} (PID {pid})",
        "sys_opened": "[system] Opened {target}",
        "sys_not_found": "[system] Not found: {target}",
        "sys_launch_error": "[system] Failed to open {target}: {error}",

        # --- auto mode ---
        "auto_tool_done": "[tool] {name} done",
        "auto_tool_running": "[tool] {name}",
        "auto_tool_calls": "[tool calls: {names} — use --auto to execute]",

        # --- token display ---
        "token_in": "in: {value}  ",
        "token_out": "out: {value}  ",

        # --- commands: memory ---
        "memory_rules_header": "Rules ({n})",
        "memory_memories_header": "Memories ({n})",

        # --- commands: lang ---
        "lang_set_zh": "lang: zh",
        "lang_set_en": "lang: en",

        # --- commands: think ---
        "think_effort_usage": "/think effort <low|medium|high>",

        # --- commands: knowledge ---
        "know_search_prompt": "Search: ",
        "know_no_matches_for": "No matches",
        "know_results_count": "━ Results ({n})",

        # --- commands: plugin ---
        "plugin_usage": "Usage: /plugin <list|info|enable|disable|create|reload>",

        # --- commands: context display ---
        "ctx_model_label": "Model:",
        "ctx_instructions_label": "Instructions:",
        "ctx_project_map_label": "Project map:",
        "ctx_branch_label": "branch:",
        "ctx_lines_suffix": "lines",
        "ctx_not_generated": "not generated",
        "ctx_no_system_prompt": "No system prompt",

        # --- commands: pin ---
        "pin_unpinned": "Unpinned: {f}",
        "pin_pinned": "Pinned: {f}",
        "pin_pinned_files": "Pinned files:",
        "pin_no_files": "No pinned files",

        # --- commands: diff ---
        "diff_header": "━━━ git diff ━━━",

        # --- commands: review ---
        "review_no_changes": "No changes to review",
        "review_requested": "Review requested ({len} chars of diff)",

        # --- commands: fix ---
        "fix_no_error": "No recent error found in conversation",
        "fix_request_sent": "Analysis request sent",

        # --- commands: rewind ---
        "rewind_nothing": "Nothing to rewind",

        # --- commands: git ---
        "git_prompt": "git ",

        # --- commands: plan ---
        "plan_usage": "Usage: /plan <task description>",
        "plan_usage_example": "Example: /plan refactor the user module with tests",
        "plan_header_mode": "╔══ Planning Mode ══╗",
        "plan_task_label": "Task:",
        "plan_step_1": "1. AI analyzes task and creates a numbered plan",
        "plan_step_2": "2. Executes each step with verification",
        "plan_step_3": "3. Uses batch_edit for atomic multi-file changes",
        "plan_started": "Plan started. AI will analyze, plan, and execute step by step.",

        # --- commands: mcp ---
        "mcp_action_list": "List connected servers & tools",
        "mcp_action_add": "Add a new MCP server",
        "mcp_action_remove": "Remove an MCP server",
        "mcp_action_restart": "Restart all MCP servers",
        "mcp_manager_title": "MCP Manager",
        "mcp_servers_header": "MCP Servers ({n})",
        "mcp_tools_header": "Tools ({n})",
        "mcp_add_args": "Arguments (space-separated):",
        "mcp_add_env": "Env vars (KEY=val, optional):",
        "mcp_remove_title": "Remove MCP server",

        # --- commands: search / history / session ---
        "search_no_matches_for": "No sessions match \"{kw}\"",
        "search_found_matches": "Found {n} session(s) matching \"{kw}\"",
        "search_action_load": "Load this session",
        "search_action_delete": "Delete",
        "search_session_label": "Session: {name} — {n} msgs",
        "history_conversation_header": "── Conversation ({n} msgs) ──",
        "session_list_title": "Sessions",

        # --- commands: export ---
        "export_user_header": "## User",
        "export_assistant_header": "## Assistant",
        "export_tool_result_prefix": "> Tool result:",

        # --- commands: model ---
        "cmd_custom_input": "[custom] Custom input",
    },
}


def set_lang(lang: str):
    global _LANG
    if lang in _STRINGS:
        _LANG = lang


def get_lang() -> str:
    return _LANG


def _(key: str, **kwargs) -> str:
    text = _STRINGS.get(_LANG, {}).get(key, _STRINGS.get("zh", {}).get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text
