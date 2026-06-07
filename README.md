# FluxLite

<p align="center">
  <img src="https://img.shields.io/badge/status-active-brightgreen" alt="Status: Active">
  <img src="https://img.shields.io/badge/python->=3.9-blue" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT">
  <img src="https://img.shields.io/badge/version-0.6.0-blueviolet" alt="Version 0.6.0">
</p>

<p align="center">
  <a href="#english"><img src="https://img.shields.io/badge/%F0%9F%87%AC%F0%9F%87%A7-English-blue?style=for-the-badge" alt="English"></a>
  <a href="#chinese"><img src="https://img.shields.io/badge/%F0%9F%87%A8%F0%9F%87%B3-中文-red?style=for-the-badge" alt="中文"></a>
</p>

---

<a name="english"></a>

## 🇬🇧 English

**FluxLite** is a lightweight, terminal-native AI coding agent. It streams responses in real time, supports plugins and MCP servers, isolates file operations in a sandbox, and ships with 34+ built-in tools.

- **Lightweight** — single EXE (~33 MB) or `pip install`, no runtime dependencies
- **Terminal-native** — streaming output, Markdown rendering, thinking display, command completion
- **Extensible** — plugin system + MCP servers + Hooks, customize at every layer
- **Safe** — sandbox isolates file ops, confirm-before-execute, quality gates

### Install

```bash
pip install fluxlite
```

Or from source:

```bash
git clone https://github.com/SVolsa/fluxlite.git
cd fluxlite
pip install -e .
```

Requirements: Python >= 3.9, an OpenAI-compatible API key.

### Quickstart

```bash
# First run — setup wizard
fluxlite --wizard

# Interactive chat
fluxlite

# One-shot query (no tool execution)
fluxlite "explain this code"

# One-shot with auto tool execution
fluxlite --auto "run the tests and fix failures"
```

### Features

| Feature | Description |
|---------|-------------|
| **Streaming Chat** | Real-time token streaming with full Markdown rendering |
| **Thinking Display** | Show AI reasoning in gray (visible / collapsed / off modes) |
| **34+ Built-in Tools** | File ops, code exec, git, search, terminal, browser, HTTP |
| **Plugin System** | Drop JSON + Python files into `~/.fluxlite/plugins/` to add tools |
| **MCP Support** | Connect external MCP servers for additional capabilities |
| **Sandbox** | File ops isolated to a temp directory; review then apply or discard |
| **Sessions** | Auto save / restore, search history, export conversations |
| **Sub-agents** | Spawn parallel sub-tasks with `spawn_agents` |
| **Planner** | `task_planner` + `self_review` toolchain for structured work |
| **Hooks** | Custom scripts triggered before / after every tool call |
| **Knowledge Base** | Semantic search over project files (TF-IDF or embedding upgrade) |
| **System Tools** | List running processes, launch applications from the agent |
| **Memory & Rules** | Persistent key-value memory with add / remove / list rules |
| **Auto-debug** | Automatic test-fix loop — run tests, analyze failures, fix, re-run |
| **Bilingual UI** | Full Chinese / English interface, switch with `/lang` |
| **Settings Persistence** | Thinking mode, tool results toggle, autocommit — all persist across restarts |
| **Project Context** | Inject `FLUXLITE.md` as system-prompt context |
| **Batch Editing** | `batch_file_edit`, `refactor`, `search_replace` for bulk code changes |

### Built-in Tools (34+)

| Category | Tools |
|----------|-------|
| **Files** | `file_read` `file_write` `file_edit` `file_append` `file_delete` `file_list` |
| **Code** | `code_executor` `run_tests` |
| **Git** | `git_status` `git_diff` `git_log` `git_add` `git_commit` |
| **Search** | `web_search` `grep_search` `glob_files` `code_search` |
| **Network** | `http_request` `file_download` `web_scrape` `browser` |
| **Terminal** | `terminal` (persistent session, Ctrl+C safe) |
| **Planning** | `spawn_agents` `task_planner` `self_review` |
| **Memory** | `memory_read` `memory_write` `rule_add` `rule_remove` `rule_list` |
| **System** | `config_set` `mcp_call` `mcp_list` `hook_run` `hook_list` |
| **Batch** | `batch_file_edit` `refactor` `search_replace` |
| **OS** | `list_processes` `launch_app` |

### Commands

```
/help    /clear   /model    /memory   /rules   /rule    /think   /compact
/toolresult  /export  /token  /truncate  /rewind  /context  /tools
/lang    /git     /autocommit  /new  /search  /sessions  /last  /plan
/mcp     /hooks   /plugin   /sandbox  /diff  /review  /fix   /pin
/init    /exit
```

- `/` triggers command completion with inline descriptions
- `Ctrl+R` for fuzzy history search
- End a line with `\` to continue typing on the next line
- Short aliases: `/s` → `/sessions`, `/q` → `/exit`

### Configuration

#### config.toml

`~/.fluxlite/config.toml`:

```toml
[api]
key = "your-api-key"
base_url = "https://api.deepseek.com"
model = "deepseek-chat"

[app]
language = "zh"           # "zh" or "en"
timeout = 60              # seconds
safe_mode = true          # sandbox + tool confirmations
```

Environment variables are also recognized: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `TAVILY_API_KEY`.

#### Persistent Settings

`~/.fluxlite/settings.json` — auto-saved on every change:

```json
{
  "thinking_mode": "off",
  "reasoning_effort": "",
  "auto_debug": true,
  "show_tool_result": false,
  "show_token_usage": false,
  "git_autocommit": false
}
```

### Thinking / Reasoning Display

FluxLite can show the AI's reasoning process in real time:

- **`/think on`** — reasoning streams as gray text, then collapses on completion
- **`/think collapsed`** — reasoning is hidden during streaming, shown collapsed after
- **`/think off`** — reasoning is never shown
- **`/think effort high`** — request extended reasoning (where supported by the model)
- **`/think display on|off`** — show the "Reasoning" header badge

The selected mode persists across restarts.

### Knowledge Base

FluxLite includes a built-in knowledge base for semantic search over project files:

- **Zero-dependency mode** — character n-gram TF-IDF (works out of the box, no extra install)
- **Embedding upgrade** — install `sentence-transformers` for neural semantic search:
  ```bash
  pip install fluxlite[knowledge]
  ```
- Auto-indexes `.py`, `.js`, `.ts`, `.rs`, `.go`, `.md`, `.json`, `.toml`, and more
- Incremental rebuild — only re-indexes changed files
- Persistent cache across sessions (`~/.fluxlite/knowledge/`)

The AI can query the knowledge base autonomously to understand your codebase.

### Project Context

Place `FLUXLITE.md` in your project root to inject it into the system prompt on every startup. Use `/init` to auto-generate one. Also supports `.fluxlite/project_memory.md` and `INSTRUCTIONS.md`.

### Plugins

See [API.md](API.md) for bilingual documentation and examples.

Create a JSON file in `~/.fluxlite/plugins/`:

```json
{
  "name": "my_tool",
  "description": "Does something useful",
  "function": {
    "name": "my_tool",
    "parameters": {
      "type": "object",
      "properties": {
        "input": { "type": "string" }
      }
    }
  },
  "python": "def my_tool(args): return {'result': f'Hello, {args[\"input\"]}!'}"
}
```

The tool is automatically registered on next startup — no config changes needed.

### MCP Servers

Connect to external MCP servers to extend FluxLite's capabilities:

```text
/mcp add    → enter server name and command interactively
/mcp list   → show connected servers and their tools
/mcp remove → disconnect a server
```

### Sandbox

In safe mode, every file write goes to a temporary directory instead of the real filesystem. You can:

- **`/sandbox status`** — show pending changes
- **`/sandbox apply`** — commit pending changes to the real filesystem
- **`/sandbox discard`** — discard all pending changes
- **`/sandbox off`** — disable sandbox for the current session

### Auto-Debug Mode

```bash
fluxlite --auto "write a fibonacci function and test it"
```

FluxLite writes code, runs tests, detects failures, analyzes error output, fixes the code, and re-runs — all autonomously. The `/autocommit` flag auto-commits each successful fix to git.

### Sub-agents & Planner

- **Sub-agents**: Ask the AI to "use spawn_agents to research X, Y, and Z, then summarize" — it spawns parallel agents, each researching a subtopic, and combines the results.
- **Planner**: The agent can use `task_planner` to break down a goal into steps, then use `self_review` to check its own work before reporting done.

### Development

```bash
# Install with all optional dependencies
pip install -e ".[tiktoken,playwright,knowledge]"

# Run tests
pytest tests/ -v

# Build standalone EXE
pyinstaller --onefile fluxlite/main.py --name fluxlite
```

### Tutorials

#### Sandbox workflow

```bash
fluxlite
> /sandbox status       # confirm sandbox is active
> edit app.py and add a new route   # changes go to temp dir
> /diff                  # review the diff
> /sandbox apply         # apply to real filesystem
```

#### Debug with auto-fix

```bash
fluxlite --auto "add input validation to the API and test it"
```

The agent writes code, runs tests, iterates on failures, and presents the final result.

#### Using the browser tool

Ask the AI to "go to example.com, take a screenshot, and describe what you see" — it will use Playwright to navigate, screenshot, and report back.

### License

MIT

---

<a name="chinese"></a>

## 🇨🇳 中文

**FluxLite** 是一款轻量级、终端原生的 AI 编码助手。支持实时流式输出、插件和 MCP 服务器扩展、文件操作沙箱隔离，内置 34+ 工具。

- **轻量** — 单文件 EXE（~33 MB）或 `pip install`，零运行时依赖
- **原生** — 流式输出、Markdown 渲染、思考过程展示、命令补全
- **可扩展** — 插件系统 + MCP 服务器 + Hooks，每个维度都可定制
- **安全** — 沙箱隔离文件操作、执行前确认、质量门禁

### 安装

```bash
pip install fluxlite
```

或从源码安装：

```bash
git clone https://github.com/SVolsa/fluxlite.git
cd fluxlite
pip install -e .
```

要求：Python >= 3.9，OpenAI 兼容的 API Key。

### 快速上手

```bash
# 首次运行 — 设置向导
fluxlite --wizard

# 交互聊天
fluxlite

# 单次问答（不执行工具）
fluxlite "解释这段代码"

# 单次问答 + 自动执行工具
fluxlite --auto "跑测试并修复失败"
```

### 功能特性

| 功能 | 说明 |
|------|------|
| **流式对话** | 实时 Token 流式输出 + Markdown 完全渲染 |
| **思考展示** | 以灰色文字显示 AI 推理过程（可见/折叠/关闭三种模式） |
| **34+ 内置工具** | 文件操作、代码执行、Git、搜索、终端、浏览器、HTTP |
| **插件系统** | 在 `~/.fluxlite/plugins/` 放入 JSON + Python 文件即可添加工具 |
| **MCP 支持** | 连接外部 MCP 服务器扩展能力 |
| **沙箱** | 文件操作隔离到临时目录，审核后应用或丢弃 |
| **会话管理** | 自动保存/恢复、搜索历史、导出对话 |
| **子代理** | 使用 `spawn_agents` 并发执行子任务 |
| **规划器** | `task_planner` + `self_review` 工具链，先规划再自查 |
| **Hooks** | 工具执行前后触发自定义脚本 |
| **知识库** | 对项目文件进行语义搜索（TF-IDF 或嵌入模型升级） |
| **系统工具** | 列出运行中的进程、从 AI 启动应用程序 |
| **记忆与规则** | 持久化键值记忆，支持添加/删除/列出规则 |
| **自动调试** | 测试-修复自动循环 — 运行测试、分析失败、修复、重跑 |
| **双语界面** | 完整中文/英文界面，通过 `/lang` 命令切换 |
| **配置持久化** | 思考模式、工具结果显示、自动提交等设置重启后保留 |
| **项目上下文** | 放置 `FLUXLITE.md` 自动注入系统提示 |
| **批量编辑** | `batch_file_edit`、`refactor`、`search_replace` 支持批量代码修改 |

### 内置工具 (34+)

| 分类 | 工具 |
|------|------|
| **文件** | `file_read` `file_write` `file_edit` `file_append` `file_delete` `file_list` |
| **代码** | `code_executor` `run_tests` |
| **Git** | `git_status` `git_diff` `git_log` `git_add` `git_commit` |
| **搜索** | `web_search` `grep_search` `glob_files` `code_search` |
| **网络** | `http_request` `file_download` `web_scrape` `browser` |
| **终端** | `terminal`（持久会话，安全处理 Ctrl+C） |
| **规划** | `spawn_agents` `task_planner` `self_review` |
| **记忆** | `memory_read` `memory_write` `rule_add` `rule_remove` `rule_list` |
| **系统** | `config_set` `mcp_call` `mcp_list` `hook_run` `hook_list` |
| **批量** | `batch_file_edit` `refactor` `search_replace` |
| **系统** | `list_processes` `launch_app` |

### 命令

```
/help    /clear   /model    /memory   /rules   /rule    /think   /compact
/toolresult  /export  /token  /truncate  /rewind  /context  /tools
/lang    /git     /autocommit  /new  /search  /sessions  /last  /plan
/mcp     /hooks   /plugin   /sandbox  /diff  /review  /fix   /pin
/init    /exit
```

- `/` 触发命令补全并显示描述
- `Ctrl+R` 模糊搜索历史
- 行末输入 `\` 可续行
- 短别名：`/s` → `/sessions`，`/q` → `/exit`

### 配置

#### config.toml

`~/.fluxlite/config.toml`：

```toml
[api]
key = "your-api-key"
base_url = "https://api.deepseek.com"
model = "deepseek-chat"

[app]
language = "zh"           # "zh" 或 "en"
timeout = 60              # 超时秒数
safe_mode = true          # 沙箱 + 工具确认
```

也支持环境变量：`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`TAVILY_API_KEY`。

#### 持久化设置

`~/.fluxlite/settings.json` — 每次修改自动保存：

```json
{
  "thinking_mode": "off",
  "reasoning_effort": "",
  "auto_debug": true,
  "show_tool_result": false,
  "show_token_usage": false,
  "git_autocommit": false
}
```

### 思考展示

FluxLite 可以实时展示 AI 的推理过程：

- **`/think on`** — 推理过程以灰色文字实时输出，完成后折叠
- **`/think collapsed`** — 推理过程流式传输时不展示，完成后以折叠状态显示
- **`/think off`** — 从不展示推理过程
- **`/think effort high`** — 请求模型进行更深入的推理（需模型支持）
- **`/think display on|off`** — 显示或隐藏"Reasoning"标签

设置重启后自动保留。

### 知识库

FluxLite 内置知识库，可以对项目文件进行语义搜索：

- **零依赖模式** — 基于字符 n-gram TF-IDF，开箱即用
- **嵌入模型升级** — 安装 `sentence-transformers` 获得语义搜索能力：
  ```bash
  pip install fluxlite[knowledge]
  ```
- 自动索引 `.py`、`.js`、`.ts`、`.rs`、`.go`、`.md`、`.json`、`.toml` 等格式
- 增量重建 — 只重新索引变更的文件
- 跨会话持久缓存（`~/.fluxlite/knowledge/`）

AI 可以自动查询知识库来理解你的代码。

### 项目上下文

在项目根目录放置 `FLUXLITE.md`，每次启动时自动注入到系统提示中。使用 `/init` 自动生成。也支持 `.fluxlite/project_memory.md` 和 `INSTRUCTIONS.md`。

### 插件

查看 [API.md](API.md) 获取中英文双语文档和示例。

在 `~/.fluxlite/plugins/` 目录下创建 JSON 文件即可注册工具：

```json
{
  "name": "my_tool",
  "description": "做点有用的事",
  "function": {
    "name": "my_tool",
    "parameters": {
      "type": "object",
      "properties": {
        "input": { "type": "string" }
      }
    }
  },
  "python": "def my_tool(args): return {'result': f'你好, {args[\"input\"]}!'}"
}
```

下次启动时自动注册，无需修改配置。

### MCP 服务器

连接外部 MCP 服务器扩展 FluxLite 的能力：

```text
/mcp add    → 交互式输入服务器名称和命令
/mcp list   → 显示已连接的服务器及其工具
/mcp remove → 断开服务器连接
```

### 沙箱

在安全模式下，所有文件写入会先进入临时目录而非真实文件系统：

- **`/sandbox status`** — 查看待处理的更改
- **`/sandbox apply`** — 将更改应用到真实文件系统
- **`/sandbox discard`** — 丢弃所有待处理的更改
- **`/sandbox off`** — 关闭当前会话的沙箱

### 自动调试

```bash
fluxlite --auto "写一个斐波那契函数并测试"
```

FluxLite 会编写代码、运行测试、检测失败、分析错误输出、修复代码并重新运行 — 全部自主完成。`/autocommit` 开关可在每次成功修复后自动提交到 Git。

### 子代理与规划器

- **子代理**：让 AI "用 spawn_agents 分别研究 X、Y、Z，然后总结" — 它会生成并发的子代理分别研究，最后合并结果。
- **规划器**：AI 可使用 `task_planner` 将目标拆解为步骤，再用 `self_review` 在报告完成前自我检查。

### 开发

```bash
# 安装全部可选依赖
pip install -e ".[tiktoken,playwright,knowledge]"

# 运行测试
pytest tests/ -v

# 编译独立 EXE
pyinstaller --onefile fluxlite/main.py --name fluxlite
```

### 教程

#### 沙箱工作流

```bash
fluxlite
> /sandbox status       # 确认沙箱已激活
> 编辑 app.py 添加新路由   # 更改进入临时目录
> /diff                  # 审查差异
> /sandbox apply         # 应用到真实文件系统
```

#### 自动调试

```bash
fluxlite --auto "给 API 添加输入验证并测试"
```

AI 编写代码、运行测试、迭代修复失败，最后展示结果。

#### 浏览器工具

让 AI "打开 example.com，截图并描述你看到的" — 它会使用 Playwright 导航、截图并报告。

### 许可

MIT
