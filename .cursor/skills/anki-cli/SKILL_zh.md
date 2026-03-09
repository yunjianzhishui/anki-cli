---
name: anki-cli-zh
description: >-
  Anki CLI 操作专家（中文）。通过 anki-cli 命令行工具查询牌组、搜索卡片、复习、导入导出、统计等全部操作。
  当用户使用中文时使用本文件。触发词：anki-cli、查卡片、查牌组、Anki 操作、复习统计、学习记录、操作 Anki。
---

# Anki CLI 操作专家

anki-cli 是本仓库的 Anki 命令行工具，与 Anki GUI 共享同一 Rust 核心引擎。
本 skill 掌握其全部能力，负责帮用户或其他 skill 执行 Anki 数据操作。

> **首次使用**：请阅读 [INSTALL_zh.md](INSTALL_zh.md) 了解如何在你的 IDE 中启用本 skill。

## 环境

| 项目 | 值 |
|------|-----|
| 工具路径 | 仓库根目录（本 skill 与 anki-cli 同仓库） |
| 执行方式 | `anki-cli <cmd>` 或 `python -m ankicli <cmd>`（需先 `pip install -e .`） |
| 虚拟环境 | `.venv/`（若使用 venv） |
| 全局选项 | `--profile <name>` · `--json` · `--path <db>` · `--verbose` · `--lang zh|en` |
| Profile | 默认 `User 1`，可用 `deck list` 等确认后按需指定 `--profile` |

## 两种连接模式

| 模式 | 条件 | 命令前缀 |
|------|------|----------|
| 直接模式 | Anki GUI **关闭** | `anki-cli <cmd>` |
| AnkiConnect | Anki GUI **运行中** + 插件 2055492159 | `anki-cli ac <cmd>` |

直连模式失败时 CLI 会自动提示切换 ac 模式。

## 执行 anki-cli 命令的标准步骤

1. 确定 profile：默认 "User 1"，多 profile 时用 `--profile "<name>"`
2. 确定模式：GUI 关闭 → 直接模式；GUI 运行 → ac 模式
3. 需要结构化输出时加 `--json`（供脚本或 skill 解析）

### 执行命令模板

```bash
anki-cli --profile "User 1" --json <子命令> [参数]
```

## 核心命令速览

完整命令列表见 [reference_zh.md](reference_zh.md)。
高频配方速查（10 个通用场景）：[recipes_zh.md](recipes_zh.md)。

| 场景 | 命令 |
|------|------|
| 列出牌组 | `deck list` / `deck tree` |
| 搜索卡片 | `search cards "<query>"` |
| 查看待复习 | `review due --deck "<deck>"` |
| 获取下一张卡 | `review next --deck "<deck>"` |
| 提交评分 | `review answer <card_id> --ease <1-4>` |
| 批量评分 | `review answer-batch --data '[{"card_id":N,"ease":M}]'` |
| 今日统计 | `stats today` |
| 牌组统计 | `stats deck` |
| 卡片详情 | `card info <card_id>` |
| 复习日志 | `card revlog <card_id>` |
| 添加笔记 | `note add --deck "<deck>" --type "<notetype>" --fields '{"Front":"x","Back":"y"}'` |
| 批量添加 | `note add-batch --file data.json` |
| FSRS 记忆状态 | `stats memory <card_id>` |
| 导出 | `export apkg --deck "<deck>" --output out.apkg` |
| 同步 | `sync collection` |

### Anki 搜索语法要点

`search cards` 使用 Anki 原生搜索语法：

| 筛选 | 语法 |
|------|------|
| 牌组 | `"deck:牌组名"` |
| 标签 | `tag:标签名` |
| 到期 | `is:due` |
| 新卡 | `is:new` |
| 暂停 | `is:suspended` |
| 字段 | `"front:关键词"` |
| 组合 | 用空格 = AND；`OR` 连接 |
| 否定 | `-is:suspended` |

## 积木哲学与缺口建议机制

**核心原则**：anki-cli 的每个命令是一块积木，不是完整解决方案。  
新需求应先尝试**组合现有积木**；做不到时，找出**缺哪块积木**，而非设计一个大而全的专用命令。

已知缺口记录在 [known-gaps.md](known-gaps.md)。

### 判断流程

1. **能否组合**：用现有命令（reference_zh.md）组合完成？→ 直接执行
2. **缺哪块积木**：组合断裂在哪一步？缺的是什么原子能力？
3. **查缺口清单**：known-gaps.md 是否已记录？
4. **建议开发积木**：向用户说明缺失的那块积木，提出最小化命令设计

### 反模式

- **不要**为特定场景设计一步到位的完整命令
- **应该**设计通用积木，让用户/AI 自由组合

## 配套教学 Skills

anki-cli 附带即用型 Skills，展示如何用 anki-cli 命令驱动学科练习与学习分析：

| Skill | 路径 | 说明 |
|-------|------|------|
| **anki-report** | `../anki-report/SKILL.md` | 学习报告分析：日报/周报/月报，七大维度洞察建议 |
| **文言文翻译** | `../wenyan-translator/SKILL.md` | 脚手架教学法 + Anki 驱动，拉卡→出题→诊断→写回 |
| **英语翻译** | `../shanghai-english-translator/SKILL.md` | 上海高考格式 + Anki 驱动，拉卡→出题→诊断→写回 |

详见 [companion-skills.md](companion-skills.md)（配套 Skills 完整指南）。

## 供其他 skill 调用

其他 skill 可在需要 Anki 数据操作时：

1. 读取本 SKILL_zh.md 获取命令格式
2. 使用 Shell 工具执行 anki-cli 命令（加 `--json` 获取结构化输出）
3. 解析 JSON 结果

### 常见集成场景

| 场景 | 推荐方式 |
|------|----------|
| 拉取待复习卡片 | `review due --deck "<deck>" --limit N --json` 或 `review next --deck "<deck>" --json` |
| 写回评分 | `review answer <card_id> --ease <1-4>` 或 `review answer-batch` |
| 查某张卡的字段 | `card info <card_id> --json` |
| 添加补充卡片 | `note add --deck ... --type ... --fields '{...}'` |
| 查今日学习量 | `stats today --profile "<name>"` |
