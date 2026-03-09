# Anki CLI

Full command-line interface for Anki — operate your collection from the terminal, alongside the GUI.

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
```

每个命令加 `--help` 查看详细用法，如 `anki-cli deck create --help`。

## 注意事项

- **与 GUI 共存**：CLI 和 Anki GUI 可以同时运行。读操作完全安全，写操作通过 SQLite WAL 模式自动排队。
- **数据位置**：默认读取 `%APPDATA%\Anki2\User 1\collection.anki2`（Windows）。
- **JSON 模式**：加 `--json` 或 `-j` 全局选项，所有输出变为 JSON，便于 AI Agent 或脚本调用。

## 许可证

本项目采用 [AGPL-3.0-or-later](LICENSE)，与 [Anki](https://github.com/ankitects/anki) 保持一致。Copyright © 2025 yunjianzhishui
