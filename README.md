# Anki CLI

Full command-line interface for Anki — operate your collection from the terminal, alongside the GUI.

---

## Design Philosophy | 设计哲学

### English

- **Same core, no fork** — Uses the official Anki Rust backend directly. No reimplementation, no drift.
- **Complement, not replace** — CLI and GUI share the same data. Use the desktop app for review, the CLI for scripting and automation.
- **Human and machine** — Rich terminal output for humans; `--json` for AI agents and scripts. One tool, two interfaces.
- **Complete coverage** — All core Anki operations from the command line: decks, cards, notes, review, import, export, sync, stats, and more.

### 中文

- **同一核心，无二次封装** — 直接使用 Anki 官方 Rust 后端，不重造轮子，不偏离主线。
- **补充而非替代** — CLI 与 GUI 共用同一套数据。桌面版刷卡片，命令行做脚本与自动化。
- **人机兼顾** — 终端美化输出给人看，`--json` 给 AI Agent 和脚本用。一个工具，两种界面。
- **功能完整** — 牌组、卡片、笔记、复习、导入导出、同步、统计等核心操作均可通过命令行完成。

---

## 安装

### 前置要求

- **Python 3.9+**
- **Anki 桌面版**（若需日常刷卡片）：从 [Anki 官方 GitHub Releases](https://github.com/ankitects/anki/releases) 下载安装，与 anki-cli 共用同一套数据。anki-cli 依赖与 **Anki 25.09.x** 兼容。

### 步骤 1: 创建虚拟环境（推荐）

```bash
cd anki-cli
python -m venv .venv

# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate
```

### 步骤 2: 安装

```bash
pip install -e .
```

这会自动安装所有依赖：
- `anki` (>=25.9,<26) — Anki 核心库，与桌面版 25.09.x 兼容
- `typer` — CLI 框架
- `rich` — 终端美化

### 步骤 3: 验证

```bash
anki-cli --version
anki-cli --help
```

## 使用

```bash
# 列出所有牌组
anki-cli deck list

# 查看待复习卡片（将 "Default" 替换为你的牌组名）
anki-cli review due --deck "Default"

# 添加卡片
anki-cli note add --front "hello" --back "你好" --deck "Default"

# 交互式复习
anki-cli review start --deck "Default"

# 查看统计
anki-cli stats today

# JSON 输出（供 AI/脚本使用）
anki-cli --json review counts
anki-cli --json search cards "is:due"
```

### 指定 Profile

```bash
# 使用非默认 profile（将 "User 1" 替换为你的 profile 名）
anki-cli --profile "User 1" deck list

# 直接指定数据库路径
anki-cli --path "C:\path\to\collection.anki2" deck list
```

### 全部命令

```
anki-cli deck       — 牌组管理（list, tree, create, rename, delete, move, info...）
anki-cli card       — 卡片操作（info, suspend, unsuspend, bury, flag, forget...）
anki-cli note       — 笔记操作（add, edit, delete, find-replace, duplicates...）
anki-cli review     — 复习流程（start, next, answer, counts, due, undo）
anki-cli search     — 搜索（cards, notes, empty-cards）
anki-cli tag        — 标签管理（list, tree, add, remove, rename, delete）
anki-cli notetype   — 笔记类型（list, info, create, copy, fields, templates...）
anki-cli import     — 导入（apkg, colpkg, csv, json）
anki-cli export     — 导出（apkg, colpkg, notes-csv, cards-csv, dataset）
anki-cli sync       — 同步（login, collection, media, status）
anki-cli stats      — 统计（today, card, deck, memory, overview）
anki-cli media      — 媒体（check, add, trash, empty-trash, restore-trash）
anki-cli config     — 配置（get, set, list, preferences）
anki-cli db         — 数据库（check, optimize, backup, info）
anki-cli scheduler  — 调度器（version, upgrade, set-v3, unbury-deck）
anki-cli lang       — 语言（set zh|en, show）
```

每个命令加 `--help` 查看详细用法，如 `anki-cli deck create --help`。

## IDE / AI 集成

anki-cli 内置 **Cursor Skill**，可在 IDE 中通过对话驱动 Anki 操作（查卡片、复习统计、添加笔记等）。

| IDE | 说明 |
|-----|------|
| **Cursor** | 用 Cursor 打开本仓库根目录，Skill 自动加载。详见 [.cursor/skills/anki-cli/INSTALL.md](.cursor/skills/anki-cli/INSTALL.md) |
| **其他 IDE** | 可将 `SKILL.md` 或 `SKILL_zh.md` 内容复制到 AI 助手的自定义指令中，或作为参考文档 |

首次使用请阅读 [.cursor/skills/anki-cli/INSTALL.md](.cursor/skills/anki-cli/INSTALL.md) 完成注册。

### 配套教学 Skills

anki-cli 附带两个即用型教学 Skill，展示如何用 anki-cli 命令驱动学科练习：

| Skill | 说明 | 触发词 |
|-------|------|--------|
| **文言文翻译** | 脚手架教学法，Anki 驱动拉卡→出题→诊断→写回 | "文言文翻译练习"、"复习文言文" |
| **英语翻译** | 上海高考格式，Anki 驱动拉卡→出题→诊断→写回 | "出英语题"、"英语翻译练习" |

详见 [.cursor/skills/anki-cli/companion-skills.md](.cursor/skills/anki-cli/companion-skills.md)。

### 语言切换 / Language

- **CLI**：首次运行会提示选择语言（中文/English）。之后可用 `anki-cli lang set zh` 或 `anki-cli lang set en` 切换；`--lang zh` / `--lang en` 可临时覆盖。
- **Skill**：AI 根据用户消息语言自动选择 SKILL.md（英文）或 SKILL_zh.md（中文）。

## 注意事项

- **与 GUI 共存**：CLI 和 Anki GUI 可以同时运行。读操作完全安全，写操作通过 SQLite WAL 模式自动排队。
- **数据位置**：默认读取 `%APPDATA%\Anki2\User 1\collection.anki2`（Windows）。
- **JSON 模式**：加 `--json` 或 `-j` 全局选项，所有输出变为 JSON，便于 AI Agent 或脚本调用。

## 许可证

本项目采用 [AGPL-3.0-or-later](LICENSE)，与 [Anki](https://github.com/ankitects/anki) 保持一致。Copyright © 2025 yunjianzhishui

---

**请关注公众号：止水学语文，获取更多使用资讯**
