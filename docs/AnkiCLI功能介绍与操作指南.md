# Anki CLI 功能介绍与操作指南

> **版本**: 0.1.0  
> **技术栈**: Python 3.9+ · Anki Rust 后端 · Typer CLI 框架 · Rich 终端美化  
> **授权协议**: AGPL-3.0-or-later

---

## 目录

1. [项目概述](#1-项目概述)
2. [安装与启动](#2-安装与启动)
3. [架构与连接模式](#3-架构与连接模式)
4. [全局选项](#4-全局选项)
5. [命令速查表](#5-命令速查表)
6. [各模块详细说明](#6-各模块详细说明)
   - [6.1 deck — 牌组管理](#61-deck--牌组管理)
   - [6.2 card — 卡片操作](#62-card--卡片操作)
   - [6.3 note — 笔记操作](#63-note--笔记操作)
   - [6.4 review — 复习流程](#64-review--复习流程)
   - [6.5 search — 搜索](#65-search--搜索)
   - [6.6 tag — 标签管理](#66-tag--标签管理)
   - [6.7 notetype — 笔记类型管理](#67-notetype--笔记类型管理)
   - [6.8 import — 数据导入](#68-import--数据导入)
   - [6.9 export — 数据导出](#69-export--数据导出)
   - [6.10 sync — 同步](#610-sync--同步)
   - [6.11 stats — 统计](#611-stats--统计)
   - [6.12 media — 媒体管理](#612-media--媒体管理)
   - [6.13 config — 配置管理](#613-config--配置管理)
   - [6.14 db — 数据库维护](#614-db--数据库维护)
   - [6.15 scheduler — 调度器管理](#615-scheduler--调度器管理)
   - [6.16 ac — AnkiConnect 模式](#616-ac--ankiconnect-模式)
7. [JSON 模式与脚本集成](#7-json-模式与脚本集成)
8. [实用场景示例](#8-实用场景示例)
9. [与 anki-bridge 的关系](#9-与-anki-bridge-的关系)
10. [故障排查](#10-故障排查)

---

## 1. 项目概述

**Anki CLI** 是一个完整的 Anki 命令行接口，与 Anki GUI 共享同一个 Rust 核心引擎。它允许你在终端中完成所有 Anki 操作：管理牌组、添加卡片、复习学习、导入导出、同步 AnkiWeb，以及查看统计信息。

### 核心优势

| 特性 | 说明 |
|------|------|
| **完整功能** | 覆盖 Anki 所有核心操作，共 17 个子命令模块、80+ 个操作 |
| **双模式连接** | 直接访问 SQLite 数据库（需关闭 GUI）或通过 AnkiConnect 代理（GUI 运行中） |
| **Rich 美化输出** | 终端表格、树形结构、彩色状态提示 |
| **JSON 模式** | 加 `--json` 即可输出结构化 JSON，方便 AI Agent 和脚本调用 |
| **FSRS 支持** | 支持查看 FSRS 记忆状态（stability、difficulty、decay） |

---

## 2. 安装与启动

### 2.1 创建虚拟环境

```bash
cd anki-cli
python -m venv .venv

# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Windows (CMD):
.venv\Scripts\activate.bat

# macOS / Linux:
source .venv/bin/activate
```

### 2.2 安装依赖

```bash
pip install -e .
```

自动安装的依赖：
- `anki` — Anki 核心库（含编译好的 Rust 引擎，约 10 MB）
- `typer>=0.9.0` — 现代 CLI 框架
- `rich>=13.0.0` — 终端美化库

### 2.3 验证安装

```bash
anki-cli --version    # 输出: anki-cli 0.1.0
anki-cli --help       # 显示所有命令
```

### 2.4 运行方式

```bash
# 方式 1: 通过 console_scripts 入口（推荐）
anki-cli <command>

# 方式 2: 通过 Python 模块
python -m ankicli <command>
```

---

## 3. 架构与连接模式

Anki CLI 支持两种互斥的数据库连接模式：

### 3.1 直接模式（Direct Mode）

```
终端 → ankicli → Anki Rust Backend → collection.anki2 (SQLite)
```

- 直接打开 `collection.anki2` 文件
- 使用 Anki 官方 Rust 后端引擎
- **要求**：Anki GUI 必须关闭（否则 SQLite 会被锁定）
- **适用**：所有子命令（deck / card / note / review / search / tag / notetype / import / export / sync / stats / media / config / db / scheduler）

### 3.2 AnkiConnect 模式

```
终端 → ankicli ac → HTTP → AnkiConnect 插件 → Anki GUI → collection.anki2
```

- 通过 HTTP 请求代理到运行中的 Anki GUI
- **要求**：Anki GUI 正在运行 + AnkiConnect 插件已安装（插件代码：`2055492159`）
- **适用**：`anki-cli ac` 子命令

### 3.3 自动检测

当直接模式因数据库锁定失败时，CLI 会自动检测 AnkiConnect 是否可用并给出提示：

```
Hint: Anki GUI is running. Use 'anki-cli ac' commands for AnkiConnect mode,
      or close Anki GUI to use direct mode.
```

### 3.4 数据库路径

默认路径按操作系统：

| 系统 | 路径 |
|------|------|
| Windows | `%APPDATA%\Anki2\{profile}\collection.anki2` |
| macOS | `~/Library/Application Support/Anki2/{profile}/collection.anki2` |
| Linux | `~/.local/share/Anki2/{profile}/collection.anki2` |

---

## 4. 全局选项

在任何子命令前都可以加上以下全局选项：

| 选项 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `--profile TEXT` | `-p` | 指定 Anki Profile 名称 | `User 1` |
| `--path TEXT` | — | 直接指定 `collection.anki2` 文件路径 | 自动检测 |
| `--json` | `-j` | 所有输出改为 JSON 格式 | 关闭 |
| `--verbose` | `-v` | 详细日志输出 | 关闭 |
| `--version` | — | 显示版本号 | — |

**示例**：

```bash
# 指定 Profile
anki-cli --profile "我的配置" deck list

# 直接指定数据库路径
anki-cli --path "D:\Anki\collection.anki2" deck list

# JSON 输出
anki-cli --json review counts

# 组合使用
anki-cli --profile "学生A" --json stats today
```

---

## 5. 命令速查表

```
anki-cli
├── deck              牌组管理
│   ├── list           列出所有牌组（含卡片数）
│   ├── tree           树形展示牌组层级
│   ├── create         创建新牌组
│   ├── rename         重命名牌组
│   ├── delete         删除牌组
│   ├── move           移动牌组到新父级
│   ├── info           查看牌组详情与配置
│   ├── select         设置当前活动牌组
│   ├── current        显示当前活动牌组
│   ├── count          显示牌组卡片数
│   ├── create-filtered    创建筛选牌组
│   └── rebuild-filtered   重建筛选牌组
│
├── card              卡片操作
│   ├── info           查看卡片详情（字段、状态、调度信息）
│   ├── stats          查看卡片统计
│   ├── revlog         查看复习日志
│   ├── move           移动卡片到其他牌组
│   ├── suspend        暂停卡片
│   ├── unsuspend      取消暂停
│   ├── bury           搁置卡片（隐藏到明天）
│   ├── unbury         取消搁置
│   ├── flag           设置卡片旗标
│   ├── forget         重置为新卡片
│   ├── set-due        设置到期日期
│   ├── reposition     调整新卡片队列位置
│   └── delete         删除卡片
│
├── note              笔记操作
│   ├── add            添加单条笔记
│   ├── add-batch      批量添加（从 JSON 文件）
│   ├── info           查看笔记详情
│   ├── edit           编辑笔记字段
│   ├── delete         删除笔记
│   ├── find-replace   查找替换
│   ├── duplicates     查找重复笔记
│   ├── fields         显示笔记字段名和值
│   └── cards          显示笔记关联的卡片
│
├── review            复习流程
│   ├── start          交互式复习（终端内）
│   ├── next           获取下一张卡片（脚本用）
│   ├── answer         提交复习评分
│   ├── answer-batch   批量提交评分
│   ├── counts         查看新/学习/复习数量
│   ├── due            列出到期卡片
│   └── undo           撤销上一次操作
│
├── search            搜索
│   ├── cards          搜索卡片
│   ├── notes          搜索笔记
│   ├── empty-cards    查找空卡片
│   └── build          构建搜索字符串（辅助）
│
├── tag               标签管理
│   ├── list           列出所有标签
│   ├── tree           树形展示标签层级
│   ├── add            添加标签到笔记
│   ├── remove         移除标签
│   ├── rename         重命名标签
│   ├── delete         删除标签
│   └── clear-unused   清理未使用的标签
│
├── notetype          笔记类型管理
│   ├── list           列出所有笔记类型（含使用数）
│   ├── info           查看详情（字段、模板）
│   ├── create         创建新类型（默认 Front/Back）
│   ├── copy           复制笔记类型
│   ├── delete         删除笔记类型
│   ├── add-field      添加字段
│   ├── remove-field   移除字段
│   ├── rename-field   重命名字段
│   ├── add-template   添加卡片模板
│   ├── remove-template 移除卡片模板
│   ├── restore        恢复为内置版本
│   └── fields         列出字段信息
│
├── import            导入数据
│   ├── apkg           导入 .apkg 包
│   ├── colpkg         导入 .colpkg（替换整个集合）
│   ├── csv            导入 CSV 文件
│   ├── json           导入 JSON 文件
│   └── csv-preview    预览 CSV 元数据
│
├── export            导出数据
│   ├── apkg           导出为 .apkg 包
│   ├── colpkg         导出整个集合为 .colpkg
│   ├── notes-csv      导出笔记为 CSV
│   ├── cards-csv      导出卡片为 CSV
│   └── dataset        导出 FSRS 训练数据集
│
├── sync              同步
│   ├── login          登录 AnkiWeb
│   ├── collection     同步集合
│   ├── media          同步媒体文件
│   ├── status         检查同步状态
│   ├── full-upload    全量上传（覆盖 AnkiWeb）
│   └── full-download  全量下载（覆盖本地）
│
├── revlog            复习日志查询
│   ├── query          按日期范围查询复习记录
│   └── summary        复习活动汇总统计
│
├── stats             统计
│   ├── today          今日学习统计
│   ├── card           单卡统计
│   ├── deck           牌组统计概览
│   ├── memory         FSRS 记忆状态
│   └── overview       全局集合概览
│
├── media             媒体管理
│   ├── check          检查媒体完整性
│   ├── add            添加媒体文件
│   ├── trash          移入回收站
│   ├── empty-trash    清空回收站
│   └── restore-trash  恢复回收站
│
├── config            配置管理
│   ├── get            获取配置值
│   ├── set            设置配置值
│   ├── list           列出所有配置
│   ├── preferences    显示偏好设置
│   └── set-preferences 修改偏好设置
│
├── db                数据库维护
│   ├── check          完整性检查与修复
│   ├── optimize       优化数据库（VACUUM + ANALYZE）
│   ├── backup         创建备份
│   └── info           显示数据库信息
│
├── scheduler         调度器管理
│   ├── version        显示当前调度器版本
│   ├── upgrade        升级到 v2 调度器
│   ├── set-v3         启用/禁用 v3 调度器
│   ├── unbury-deck    取消搁置牌组内所有卡片
│   └── custom-study   自定义学习（扩展每日限额）
│
└── ac                AnkiConnect 模式（GUI 运行时使用）
    ├── decks          列出牌组
    ├── due            查看到期卡片
    ├── counts         今日复习数
    ├── search         搜索卡片
    ├── add            添加笔记
    ├── answer         提交评分
    ├── suspend        暂停卡片
    ├── unsuspend      取消暂停
    ├── tags           列出标签
    ├── add-tags       添加标签
    ├── notetypes      列出笔记类型
    ├── sync           触发同步
    └── delete-notes   删除笔记
```

---

## 6. 各模块详细说明

### 6.1 deck — 牌组管理

管理 Anki 牌组（Deck）的创建、查询、移动、删除等操作。

#### 6.1.1 `deck list` — 列出所有牌组

```bash
anki-cli deck list
```

输出一张包含 ID、名称、卡片数的表格。

#### 6.1.2 `deck tree` — 树形展示牌组层级

```bash
anki-cli deck tree
```

以树形结构展示牌组层级关系，并显示各级别的新卡、学习中、待复习数量。

#### 6.1.3 `deck create` — 创建新牌组

```bash
anki-cli deck create "高中文言300"
anki-cli deck create "语文::文言文::高中"    # 使用 :: 创建嵌套牌组
```

#### 6.1.4 `deck rename` — 重命名牌组

```bash
anki-cli deck rename "旧名称" "新名称"
```

#### 6.1.5 `deck delete` — 删除牌组

```bash
anki-cli deck delete "要删除的牌组"
```

#### 6.1.6 `deck move` — 移动牌组到新父级

```bash
anki-cli deck move "子牌组" --parent "父牌组"
```

#### 6.1.7 `deck info` — 查看牌组详情

```bash
anki-cli deck info "高中文言300"
```

显示：ID、名称、卡片总数、配置名称、每日新卡上限、每日复习上限、是否为筛选牌组。

#### 6.1.8 `deck select` / `deck current` — 管理活动牌组

```bash
anki-cli deck select "高中文言300"   # 设置当前牌组
anki-cli deck current               # 查看当前牌组
```

#### 6.1.9 `deck count` — 卡片计数

```bash
anki-cli deck count "高中文言300"
```

分别显示本级卡片数和含子牌组的总数。

#### 6.1.10 `deck create-filtered` / `deck rebuild-filtered` — 筛选牌组

```bash
anki-cli deck create-filtered "错题本" --search "tag:错题 is:due"
anki-cli deck rebuild-filtered "错题本"
```

---

### 6.2 card — 卡片操作

对单张或多张卡片进行查看、状态修改、移动等操作。多卡片 ID 以逗号分隔传入。

#### 6.2.1 `card info` — 查看卡片详情

```bash
anki-cli card info 1234567890
```

显示：卡片 ID、笔记 ID、所属牌组、笔记类型、队列状态、类型、到期日、间隔、简易因子、复习次数、遗忘次数、所有字段值、标签。

#### 6.2.2 `card stats` — 卡片统计

```bash
anki-cli card stats 1234567890
```

显示平均用时、总用时等统计信息。

#### 6.2.3 `card revlog` — 复习日志

```bash
anki-cli card revlog 1234567890
```

展示该卡片的完整复习历史：时间、类型、评分、间隔、简易因子、用时。

#### 6.2.4 `card move` — 移动卡片

```bash
anki-cli card move "1111,2222,3333" --deck "目标牌组"
```

#### 6.2.5 `card suspend` / `card unsuspend` — 暂停/恢复

```bash
anki-cli card suspend "1111,2222"
anki-cli card unsuspend "1111,2222"
```

暂停的卡片不会出现在复习队列中。

#### 6.2.6 `card bury` / `card unbury` — 搁置/取消搁置

```bash
anki-cli card bury "1111,2222"      # 隐藏到明天
anki-cli card unbury "1111,2222"
```

#### 6.2.7 `card flag` — 设置旗标

```bash
anki-cli card flag "1111,2222" --flag 1
```

旗标编号：0=无、1=红、2=橙、3=绿、4=蓝、5=粉、6=青、7=紫。

#### 6.2.8 `card forget` — 重置为新卡片

```bash
anki-cli card forget "1111,2222"
```

将卡片的学习进度完全重置。

#### 6.2.9 `card set-due` — 设置到期日

```bash
anki-cli card set-due "1111,2222" --days 0    # 今天到期
anki-cli card set-due "1111,2222" --days 3    # 3 天后到期
```

#### 6.2.10 `card reposition` — 调整新卡片位置

```bash
anki-cli card reposition "1111,2222" --start 0 --step 1 --randomize
```

#### 6.2.11 `card delete` — 删除卡片

```bash
anki-cli card delete "1111,2222"
```

同时删除成为孤儿的笔记。

---

### 6.3 note — 笔记操作

笔记（Note）是卡片（Card）的数据源，一条笔记可以生成多张卡片。

#### 6.3.1 `note add` — 添加单条笔记

```bash
# 简单模式（Basic 类型）
anki-cli note add --front "鄙" --back "轻视；边境" --deck "高中文言300" --tags "高频词"

# 自定义字段
anki-cli note add --type "Cloze" --fields "Text={{c1::间接引语}}用陈述语气,Tags=语法" --deck "英语"

# 指定笔记类型
anki-cli note add --front "词" --back "释义" --type "Basic (and reversed card)" --deck "Default"
```

参数说明：
- `--front / -f`：正面字段（适用于 Basic 类型）
- `--back / -b`：背面字段
- `--deck / -d`：目标牌组（默认 "Default"）
- `--type / -t`：笔记类型（默认 "Basic"）
- `--fields`：自定义字段，格式为 `key=value,key=value`
- `--tags`：空格分隔的标签

#### 6.3.2 `note add-batch` — 批量添加

```bash
anki-cli note add-batch --file notes.json --deck "高中文言300" --type "Basic"
```

JSON 文件格式支持两种：

```json
[
  {"front": "鄙", "back": "轻视"},
  {"front": "既", "back": "已经；……之后"}
]
```

或更灵活的格式：

```json
[
  {"fields": {"Front": "鄙", "Back": "轻视"}, "tags": "高频词 文言文"},
  {"fields": {"Front": "既", "Back": "已经"}, "tags": "高频词"}
]
```

#### 6.3.3 `note info` — 查看笔记详情

```bash
anki-cli note info 1234567890
```

#### 6.3.4 `note edit` — 编辑字段

```bash
anki-cli note edit 1234567890 --field "Back" --value "新的释义内容"
```

#### 6.3.5 `note delete` — 删除笔记

```bash
anki-cli note delete "1111,2222,3333"
```

#### 6.3.6 `note find-replace` — 查找替换

```bash
# 简单文本替换
anki-cli note find-replace --search "旧文本" --replace "新文本"

# 限定范围和字段
anki-cli note find-replace --search "错误" --replace "正确" --query "deck:高中文言300" --field "Back"

# 正则表达式
anki-cli note find-replace --search "\b(\d+)\b" --replace "[$1]" --regex --case
```

#### 6.3.7 `note duplicates` — 查找重复

```bash
anki-cli note duplicates --field "Front" --search "deck:Default"
```

#### 6.3.8 `note fields` / `note cards` — 辅助查询

```bash
anki-cli note fields 1234567890     # 显示字段名和值
anki-cli note cards 1234567890      # 显示关联的卡片
```

---

### 6.4 review — 复习流程

提供交互式复习和程序化复习接口。

#### 6.4.1 `review start` — 交互式复习

```bash
anki-cli review start                        # 复习当前牌组
anki-cli review start --deck "高中文言300"    # 指定牌组
```

交互流程：
1. 显示当前剩余数量（新卡 / 学习中 / 待复习）
2. 显示正面内容（Question 面板）
3. 按 Enter 翻转显示答案（Answer 面板）
4. 选择评分：
   - `1` — Again（重来）
   - `2` — Hard（困难）
   - `3` — Good（良好）
   - `4` — Easy（简单）
   - `u` — Undo（撤销上一张）
   - `q` — Quit（退出）

支持 Rich 美化界面（彩色面板）和纯文本回退模式。

#### 6.4.2 `review next` — 获取下一张卡片（脚本用）

```bash
anki-cli review next --deck "高中文言300"
anki-cli --json review next --deck "高中文言300"    # JSON 模式含完整字段和标签
```

JSON 输出示例：
```json
{
  "card_id": 1234567890,
  "note_id": 9876543210,
  "deck_id": 1111111111,
  "queue": 2,
  "new_count": 5,
  "learn_count": 3,
  "review_count": 12,
  "fields": {"Front": "鄙", "Back": "轻视"},
  "tags": ["高频词", "文言文"]
}
```

#### 6.4.3 `review answer` — 提交评分

```bash
anki-cli review answer 1234567890 --ease 3    # Good
```

评分说明：1=Again, 2=Hard, 3=Good, 4=Easy。

#### 6.4.4 `review answer-batch` — 批量评分

```bash
anki-cli review answer-batch --data '[{"card_id": 111, "ease": 3}, {"card_id": 222, "ease": 4}]'
```

#### 6.4.5 `review counts` — 查看复习数量

```bash
anki-cli review counts
anki-cli review counts --deck "高中文言300"
```

输出：新卡数、学习中、待复习、总计。

#### 6.4.6 `review due` — 列出到期卡片

```bash
anki-cli review due --deck "高中文言300" --limit 50
```

#### 6.4.7 `review undo` — 撤销

```bash
anki-cli review undo
```

---

### 6.5 search — 搜索

使用 Anki 原生搜索语法查找卡片和笔记。

#### 6.5.1 `search cards` — 搜索卡片

```bash
anki-cli search cards "is:due"                          # 所有到期卡片
anki-cli search cards "deck:高中文言300 is:new"          # 某牌组新卡
anki-cli search cards "tag:高频词 -is:suspended"         # 有标签且未暂停
anki-cli search cards "front:鄙" --limit 10             # 限制结果数
anki-cli search cards "added:7" --order                  # 最近 7 天添加，按集合排序
```

#### 6.5.2 `search notes` — 搜索笔记

```bash
anki-cli search notes "deck:高中文言300"
anki-cli search notes "tag:错题" --limit 100
```

#### 6.5.3 `search empty-cards` — 查找空卡片

```bash
anki-cli search empty-cards
```

找出没有内容的卡片，按笔记类型和模板分组统计。

#### 6.5.4 `search build` — 构建搜索字符串

```bash
anki-cli search build "is:due" "deck:Default" --joiner AND
anki-cli search build "tag:高频词" "tag:文言文" --joiner OR
```

辅助工具，将多个搜索条件组合为合法的搜索字符串。

#### 常用 Anki 搜索语法

| 语法 | 含义 |
|------|------|
| `is:due` | 到期卡片 |
| `is:new` | 新卡片 |
| `is:learn` | 学习中 |
| `is:review` | 复习卡 |
| `is:suspended` | 已暂停 |
| `is:buried` | 已搁置 |
| `deck:名称` | 指定牌组 |
| `tag:标签` | 指定标签 |
| `front:内容` | 正面包含 |
| `back:内容` | 背面包含 |
| `added:N` | 最近 N 天添加 |
| `rated:N` | 最近 N 天评分过 |
| `rated:N:1` | 最近 N 天评为 Again |
| `flag:N` | 指定旗标 |
| `note:类型名` | 指定笔记类型 |
| `-条件` | 取反（NOT） |

---

### 6.6 tag — 标签管理

#### 6.6.1 `tag list` / `tag tree`

```bash
anki-cli tag list     # 平铺列出所有标签
anki-cli tag tree     # 树形展示标签层级（支持 :: 嵌套）
```

#### 6.6.2 `tag add` / `tag remove`

```bash
anki-cli tag add "1111,2222,3333" --tags "高频词 重点"
anki-cli tag remove "1111,2222" --tags "旧标签"
```

注意：此处传入的是 **笔记 ID**（不是卡片 ID）。

#### 6.6.3 `tag rename` / `tag delete`

```bash
anki-cli tag rename "旧标签名" "新标签名"
anki-cli tag delete "要删除的标签"
```

#### 6.6.4 `tag clear-unused`

```bash
anki-cli tag clear-unused    # 清理所有未被任何笔记引用的标签
```

---

### 6.7 notetype — 笔记类型管理

笔记类型定义了字段结构和卡片模板。

#### 6.7.1 `notetype list` — 列出所有类型

```bash
anki-cli notetype list
```

显示 ID、名称、使用计数。

#### 6.7.2 `notetype info` — 查看详情

```bash
anki-cli notetype info "Basic"
```

显示字段列表、模板列表、CSS 长度、排序字段。

#### 6.7.3 `notetype create` — 创建新类型

```bash
anki-cli notetype create "我的自定义类型"
```

默认创建 Front/Back 两个字段和一个 Card 1 模板。

#### 6.7.4 `notetype copy` — 复制类型

```bash
anki-cli notetype copy "Basic" "Basic (自定义)"
```

#### 6.7.5 字段操作

```bash
anki-cli notetype add-field "Basic" "Example"          # 添加字段
anki-cli notetype remove-field "Basic" "Example"       # 移除字段
anki-cli notetype rename-field "Basic" "Front" "问题"   # 重命名字段
```

#### 6.7.6 模板操作

```bash
anki-cli notetype add-template "Basic" "Card 2"       # 添加模板
anki-cli notetype remove-template "Basic" "Card 2"    # 移除模板
```

#### 6.7.7 `notetype fields` — 列出字段信息

```bash
anki-cli notetype fields "Basic"
```

显示字段索引、名称、是否为排序字段。

#### 6.7.8 `notetype restore` — 恢复为内置版本

```bash
anki-cli notetype restore "Basic"
```

#### 6.7.9 `notetype delete` — 删除类型

```bash
anki-cli notetype delete "不需要的类型"
```

**危险操作**：会同时删除该类型的所有笔记！会有确认提示。

---

### 6.8 import — 数据导入

#### 6.8.1 `import apkg` — 导入 Anki 包

```bash
anki-cli import apkg "shared_deck.apkg"
```

支持合并笔记类型、更新已有笔记、保留调度信息。

#### 6.8.2 `import colpkg` — 导入集合包

```bash
anki-cli import colpkg "backup.colpkg"
```

**危险操作**：会替换整个集合！有确认提示。

#### 6.8.3 `import csv` — 导入 CSV

```bash
anki-cli import csv "words.csv" --deck "英语单词" --type "Basic"
```

自动检测分隔符和列映射。

#### 6.8.4 `import json` — 导入 JSON

```bash
anki-cli import json "notes.json"
```

#### 6.8.5 `import csv-preview` — 预览 CSV

```bash
anki-cli import csv-preview "words.csv"
```

在实际导入前预览分隔符、列数、映射关系。

---

### 6.9 export — 数据导出

#### 6.9.1 `export apkg` — 导出 Anki 包

```bash
# 导出单个牌组
anki-cli export apkg --output "backup.apkg" --deck "高中文言300"

# 导出所有牌组
anki-cli export apkg --output "all_decks.apkg"

# 不含调度信息（分享用）
anki-cli export apkg --output "share.apkg" --deck "高中文言300" --no-scheduling

# 不含媒体
anki-cli export apkg --output "light.apkg" --no-media

# 旧版格式
anki-cli export apkg --output "legacy.apkg" --legacy
```

#### 6.9.2 `export colpkg` — 导出集合包

```bash
anki-cli export colpkg --output "full_backup.colpkg"
anki-cli export colpkg --output "no_media.colpkg" --no-media
```

#### 6.9.3 `export notes-csv` — 导出笔记 CSV

```bash
anki-cli export notes-csv --output "notes.csv" --deck "高中文言300"
anki-cli export notes-csv --output "notes.csv" --html --with-deck --with-notetype --with-guid
```

可选列：标签、牌组名、笔记类型名、GUID。

#### 6.9.4 `export cards-csv` — 导出卡片 CSV

```bash
anki-cli export cards-csv --output "cards.csv" --deck "高中文言300"
```

#### 6.9.5 `export dataset` — 导出 FSRS 训练数据

```bash
anki-cli export dataset --output "research_data" --min-entries 5
```

导出格式适用于 FSRS 算法研究和训练。

---

### 6.10 sync — 同步

与 AnkiWeb 进行集合和媒体同步。

#### 6.10.1 `sync login` — 登录

```bash
anki-cli sync login --user "email@example.com" --pass
```

密码会提示安全输入（不回显）。成功后显示 hkey 令牌。

#### 6.10.2 `sync collection` — 同步集合

```bash
anki-cli sync collection --user "email@example.com" --pass
anki-cli sync collection --user "email@example.com" --pass --no-media   # 不同步媒体
```

#### 6.10.3 `sync media` — 仅同步媒体

```bash
anki-cli sync media --user "email@example.com" --pass
```

#### 6.10.4 `sync status` — 检查同步状态

```bash
anki-cli sync status --user "email@example.com" --pass
```

#### 6.10.5 `sync full-upload` / `sync full-download`

```bash
# 用本地覆盖 AnkiWeb
anki-cli sync full-upload --user "email@example.com" --pass

# 用 AnkiWeb 覆盖本地
anki-cli sync full-download --user "email@example.com" --pass
```

**危险操作**：单向覆盖，有确认提示。

---

### 6.11 revlog — 复习日志查询

查询 Anki 复习日志（revlog 表），是构建"学习记录分析"类需求的核心积木。

#### 6.11.1 `revlog query` — 按日期范围查询

```bash
# 过去 1 天（使用 Anki 换日边界）
anki-cli revlog query --days 1

# 指定日期范围
anki-cli revlog query --since 2026-03-01 --until 2026-03-08

# 去重（每张卡只保留第一次复习记录）
anki-cli revlog query --days 1 --unique

# JSON 输出（供脚本/AI 解析）
anki-cli --json revlog query --days 1 --unique --limit 50
```

输出字段：`review_id`、`card_id`、`time`、`type`（learn/review/relearn/cram）、`rating`（Again/Hard/Good/Easy）、`interval`、`last_interval`、`ease_factor`、`taken_ms`

**组合示例**：查询"昨天学了哪些英语卡片"

```bash
# Step 1: 获取昨天所有复习的 card_id
anki-cli --profile "操东瀚" --json revlog query --days 1 --unique

# Step 2: 用 card_id 在英语牌组中搜索详情
anki-cli --profile "操东瀚" search cards "cid:1234567890 deck:英语"
```

#### 6.11.2 `revlog summary` — 复习活动汇总

```bash
anki-cli revlog summary --days 1
anki-cli revlog summary --since 2026-03-01 --until 2026-03-08
```

输出：总复习次数、去重卡片数、总用时、各评分次数（Again/Hard/Good/Easy）、各类型次数（learn/review/relearn）。

---

### 6.12 stats — 统计

#### 6.11.1 `stats today` — 今日统计

```bash
anki-cli stats today
```

显示今日已学习数量、剩余新卡、学习中、待复习、总待处理。

#### 6.11.2 `stats card` — 单卡统计

```bash
anki-cli stats card 1234567890
```

#### 6.11.3 `stats deck` — 牌组统计

```bash
anki-cli stats deck                                # 全部牌组
anki-cli stats deck --deck "高中文言300"            # 筛选特定牌组
```

以扁平化表格展示各牌组的新/学习/复习数量。

#### 6.11.4 `stats memory` — FSRS 记忆状态

```bash
anki-cli stats memory 1234567890
```

显示 FSRS 算法的核心参数：
- **desired_retention**: 目标保留率
- **stability**: 记忆稳定性（天数）
- **difficulty**: 记忆难度
- **decay**: 衰减率

#### 6.11.5 `stats overview` — 集合概览

```bash
anki-cli stats overview
```

显示总卡片数、总笔记数、总牌组数、调度器版本、集合路径。

---

### 6.13 media — 媒体管理

#### 6.12.1 `media check` — 检查媒体完整性

```bash
anki-cli media check
```

检测缺失文件、未使用文件、重命名的文件、超大文件。

#### 6.12.2 `media add` — 添加文件

```bash
anki-cli media add "path/to/image.png"
```

#### 6.12.3 `media trash` / `media empty-trash` / `media restore-trash`

```bash
anki-cli media trash "file1.png,file2.mp3"
anki-cli media empty-trash        # 永久删除
anki-cli media restore-trash      # 恢复
```

---

### 6.14 config — 配置管理

#### 6.13.1 读取和设置配置

```bash
anki-cli config get "sortType"
anki-cli config set "sortType" '"noteFld"'    # 值为 JSON 编码
anki-cli config list                          # 列出全部
```

#### 6.13.2 偏好设置

```bash
anki-cli config preferences                  # 查看所有偏好
```

显示调度、复习、编辑三类偏好：
- `learn_ahead_secs` — 提前学习秒数
- `new_timezone` — 新时区设置
- `day_learn_first` — 优先学习当日卡
- `time_limit_secs` — 计时器限制
- `show_remaining_due_counts` — 显示剩余数
- `show_intervals_on_buttons` — 按钮上显示间隔
- `adding_defaults_to_current_deck` — 添加时默认当前牌组
- `paste_strips_formatting` — 粘贴时去除格式

```bash
anki-cli config set-preferences --key "learn_ahead_secs" --value 1200
anki-cli config set-preferences --key "show_intervals_on_buttons" --value true
```

---

### 6.15 db — 数据库维护

#### 6.14.1 `db check` — 完整性检查

```bash
anki-cli db check
```

运行完整的数据库完整性检查并自动修复。

#### 6.14.2 `db optimize` — 优化

```bash
anki-cli db optimize
```

执行 SQLite 的 VACUUM 和 ANALYZE，减少碎片、提升性能。

#### 6.14.3 `db backup` — 备份

```bash
anki-cli db backup                                  # 默认备份到 Anki 备份目录
anki-cli db backup --dir "D:\backups"               # 指定备份目录
anki-cli db backup --no-force                       # 如果最近已备份则跳过
```

#### 6.14.4 `db info` — 数据库信息

```bash
anki-cli db info
```

显示路径、文件大小、Profile、调度器版本、卡片/笔记/牌组数量、Schema 变更状态。

---

### 6.16 scheduler — 调度器管理

#### 6.15.1 `scheduler version` — 查看版本

```bash
anki-cli scheduler version
```

#### 6.15.2 `scheduler upgrade` — 升级到 v2

```bash
anki-cli scheduler upgrade
```

#### 6.15.3 `scheduler set-v3` — 启用/禁用 v3（FSRS）

```bash
anki-cli scheduler set-v3 true     # 启用
anki-cli scheduler set-v3 false    # 禁用
```

#### 6.15.4 `scheduler unbury-deck` — 取消牌组搁置

```bash
anki-cli scheduler unbury-deck "高中文言300"
```

取消该牌组内所有被搁置的卡片。

#### 6.15.5 `scheduler custom-study` — 自定义学习

```bash
# 查看可扩展的额度
anki-cli scheduler custom-study "高中文言300"

# 扩展每日限额
anki-cli scheduler custom-study "高中文言300" --extend-new 10 --extend-review 20
```

---

### 6.17 ac — AnkiConnect 模式

当 Anki GUI 正在运行时，通过 AnkiConnect 插件进行操作。所有 `ac` 子命令通过 HTTP 代理到 `http://127.0.0.1:8765`。

**前提条件**：
1. Anki GUI 正在运行
2. 安装了 AnkiConnect 插件（插件代码：`2055492159`）

#### 常用操作

```bash
anki-cli ac decks                                    # 列出牌组
anki-cli ac due --deck "高中文言300" --limit 30       # 查看到期卡片
anki-cli ac counts                                   # 今日已复习数
anki-cli ac search "is:due deck:Default"             # 搜索
anki-cli ac add --front "词" --back "义" --deck "Default" --tags "新增"   # 添加笔记
anki-cli ac answer 1234567890 --ease 3               # 提交评分
anki-cli ac suspend "1111,2222"                      # 暂停
anki-cli ac unsuspend "1111,2222"                    # 恢复
anki-cli ac tags                                     # 列出标签
anki-cli ac add-tags "1111,2222" --tags "重要"       # 添加标签
anki-cli ac notetypes                                # 列出笔记类型
anki-cli ac sync                                     # 触发同步
anki-cli ac delete-notes "1111,2222"                 # 删除笔记
```

---

## 7. JSON 模式与脚本集成

加上 `--json` 或 `-j` 全局选项，所有输出统一为 JSON 格式，方便 AI Agent、脚本或其他程序解析。

### 7.1 JSON 输出示例

```bash
$ anki-cli --json review counts --deck "高中文言300"
```

```json
{
  "new": 5,
  "learning": 3,
  "review": 12,
  "total": 20
}
```

```bash
$ anki-cli --json deck list
```

```json
[
  {"id": 1, "name": "Default", "cards": 0},
  {"id": 1234567890, "name": "高中文言300", "cards": 285}
]
```

### 7.2 在脚本中使用

```python
import subprocess
import json

result = subprocess.run(
    ["anki-cli", "--json", "review", "next", "--deck", "高中文言300"],
    capture_output=True, text=True
)
card = json.loads(result.stdout)
print(f"下一张卡片: {card['fields']['Front']}")
```

```bash
# Bash 中配合 jq 使用
anki-cli --json review due --deck "高中文言300" | jq '.[].front'
```

### 7.3 状态响应格式

成功操作：
```json
{"status": "ok", "message": "Added note (ID: 12345) to deck 'Default'"}
```

失败操作：
```json
{"status": "error", "message": "Deck 'xxx' not found"}
```

---

## 8. 实用场景示例

### 场景 1: 每日复习工作流

```bash
# 1. 查看今日统计
anki-cli stats today

# 2. 查看到期卡片分布
anki-cli stats deck

# 3. 开始交互式复习
anki-cli review start --deck "高中文言300"

# 4. 复习后查看成果
anki-cli stats today
```

### 场景 2: 批量添加知识卡片

```bash
# 1. 准备 JSON 文件 (notes.json)
# 2. 批量导入
anki-cli note add-batch --file notes.json --deck "英语单词" --type "Basic"

# 3. 验证
anki-cli deck count "英语单词"
```

### 场景 3: 数据迁移与备份

```bash
# 1. 备份数据库
anki-cli db backup --dir "D:\AnkiBackup"

# 2. 导出牌组为 apkg
anki-cli export apkg --output "高中文言300.apkg" --deck "高中文言300"

# 3. 导出为 CSV（便于外部分析）
anki-cli export notes-csv --output "notes.csv" --deck "高中文言300" --with-deck --with-notetype

# 4. 导出 FSRS 训练数据
anki-cli export dataset --output "fsrs_data" --min-entries 3
```

### 场景 4: AI Agent 驱动的自适应学习

```bash
# 1. AI 获取到期卡片
anki-cli --json review next --deck "高中文言300"

# 2. AI 展示问题、收集学生回答、评估

# 3. AI 提交评分
anki-cli review answer 1234567890 --ease 3

# 4. AI 查看 FSRS 记忆状态
anki-cli --json stats memory 1234567890
```

### 场景 5: 集合维护

```bash
# 1. 数据库完整性检查
anki-cli db check

# 2. 优化数据库
anki-cli db optimize

# 3. 媒体检查
anki-cli media check

# 4. 清理未使用的标签
anki-cli tag clear-unused

# 5. 查找并清理空卡片
anki-cli search empty-cards
```

### 场景 6: GUI 运行时操作（AnkiConnect）

```bash
# Anki GUI 正在运行时
anki-cli ac decks                            # 列出牌组
anki-cli ac due --deck "Default"             # 查看到期卡片
anki-cli ac add --front "新词" --back "释义" --deck "Default"   # 快速添加
anki-cli ac sync                             # 触发同步
```

---

## 9. 与 anki-bridge 的关系

本项目工作空间中包含两个 Anki 相关组件：

| 组件 | 定位 | 连接方式 | 调用方 |
|------|------|----------|--------|
| **anki-cli** | 完整 CLI 工具 | 直接 SQLite + AnkiConnect | 终端用户、脚本 |
| **anki-bridge** | 轻量脚本集 | 仅 AnkiConnect | Cursor Skills、自动化脚本 |

- `anki-bridge/` 目录下包含 `get_due_cards.py`、`add_note.py`、`answer_card.py` 等独立脚本
- Skills（如 `anki-due-cards`、`anki-card-collector`、`wenyan-translator` 等）调用的是 `anki-bridge`
- `anki-cli` 是更完整的替代方案，可覆盖 `anki-bridge` 的所有功能

---

## 10. 故障排查

### 问题 1: "database is locked" 错误

**原因**: Anki GUI 正在运行，锁定了 SQLite 数据库。

**解决方案**:
- 方案 A: 关闭 Anki GUI，再使用 `anki-cli` 直接模式
- 方案 B: 安装 AnkiConnect 插件，使用 `anki-cli ac` 子命令

### 问题 2: "collection not found" 错误

**原因**: 指定的 Profile 不存在或路径错误。

**解决方案**:
```bash
# 检查可用的 Profile
anki-cli --help   # 默认 Profile 为 "User 1"

# 直接指定路径
anki-cli --path "C:\Users\你的用户名\AppData\Roaming\Anki2\User 1\collection.anki2" deck list
```

### 问题 3: AnkiConnect 不可用

**原因**: Anki GUI 未运行或未安装 AnkiConnect 插件。

**解决方案**:
1. 打开 Anki GUI
2. 工具 → 插件 → 获取插件 → 输入代码 `2055492159` → 安装
3. 重启 Anki
4. 使用 `anki-cli ac` 命令

### 问题 4: 笔记类型字段不匹配

**原因**: 使用 `--front/--back` 但笔记类型只有一个字段。

**解决方案**:
```bash
# 先查看笔记类型的字段
anki-cli notetype fields "你的笔记类型"

# 使用 --fields 参数手动映射
anki-cli note add --type "Cloze" --fields "Text={{c1::内容}}" --deck "Default"
```

### 问题 5: 中文路径问题

Windows 下如果 Anki 数据路径包含中文，可以使用 `--path` 直接指定：

```bash
anki-cli --path "C:\Users\用户\AppData\Roaming\Anki2\User 1\collection.anki2" deck list
```

---

> **提示**: 每个命令都支持 `--help` 选项查看详细用法，例如 `anki-cli deck create --help`。
