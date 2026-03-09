# anki-cli 完整命令参考

> 执行前缀：`anki-cli [全局选项] <子命令>`（需先 `pip install -e .`）

## 全局选项

| 选项 | 缩写 | 说明 | 默认 |
|------|------|------|------|
| `--profile TEXT` | `-p` | Anki Profile 名称 | `User 1` |
| `--path TEXT` | — | collection.anki2 路径 | 自动检测 |
| `--json` | `-j` | JSON 输出 | 关 |
| `--lang zh|en` | `-l` | 界面语言 | 配置文件 |
| `--verbose` | `-v` | 详细日志 | 关 |
| `--version` | — | 版本号 | — |

---

## deck — 牌组管理

| 命令 | 说明 | 关键参数 |
|------|------|----------|
| `deck list` | 列出所有牌组 | — |
| `deck tree` | 树形展示层级 | — |
| `deck create "<name>"` | 创建牌组（`::` 嵌套） | — |
| `deck rename "<old>" "<new>"` | 重命名 | — |
| `deck delete "<name>"` | 删除 | — |
| `deck move "<name>" --parent "<parent>"` | 移动 | — |
| `deck info "<name>"` | 详情与配置 | — |
| `deck select "<name>"` | 设为当前牌组 | — |
| `deck current` | 显示当前牌组 | — |
| `deck count "<name>"` | 卡片数 | — |
| `deck create-filtered "<name>" --query "<q>"` | 创建筛选牌组 | `--limit` |
| `deck rebuild-filtered "<name>"` | 重建筛选牌组 | — |

## card — 卡片操作

| 命令 | 说明 | 关键参数 |
|------|------|----------|
| `card info <id>` | 字段、状态、调度 | — |
| `card info-batch "<ids>"` | 批量查询卡片详情 | 逗号分隔 ID |
| `card stats <id>` | 统计（平均/总用时） | — |
| `card revlog <id>` | 复习日志 | — |
| `card move "<ids>" --deck "<deck>"` | 移动卡片 | 逗号分隔 ID |
| `card suspend "<ids>"` | 暂停 | — |
| `card unsuspend "<ids>"` | 取消暂停 | — |
| `card bury "<ids>"` | 搁置到明天 | — |
| `card unbury "<ids>"` | 取消搁置 | — |
| `card flag "<ids>" --flag <0-7>` | 设旗标 | 0=无,1=红,2=橙... |
| `card forget "<ids>"` | 重置为新卡 | — |
| `card set-due "<ids>" --days <N>` | 设到期日 | 0=今天 |
| `card reposition "<ids>" --start <N>` | 调整新卡位置 | `--step`, `--randomize` |
| `card delete "<ids>"` | 删除 | — |

## note — 笔记操作

| 命令 | 说明 | 关键参数 |
|------|------|----------|
| `note add --deck "<d>" --type "<t>" --fields '<json>'` | 添加笔记 | `--tags` |
| `note add-batch --file <f>` | 从 JSON 批量添加 | `--deck`, `--type` |
| `note info <id>` | 笔记详情 | — |
| `note edit <id> --field "<name>" --value "<val>"` | 编辑字段 | — |
| `note delete "<ids>"` | 删除笔记 | — |
| `note find-replace --field "<f>" --find "<s>" --replace "<r>"` | 查找替换 | `--query` |
| `note duplicates --field "<f>"` | 查找重复 | `--query` |
| `note fields <id>` | 显示字段名和值 | — |
| `note cards <id>` | 关联的卡片 | — |

## review — 复习流程

| 命令 | 说明 | 关键参数 |
|------|------|----------|
| `review start` | 交互式终端复习 | `--deck` |
| `review next` | 获取下一张卡（脚本用） | `--deck` |
| `review answer <card_id> --ease <1-4>` | 提交评分 | 1=Again,2=Hard,3=Good,4=Easy |
| `review answer-batch --data '<json>'` | 批量评分 | JSON 数组 |
| `review counts` | 新/学习/复习数量 | `--deck` |
| `review due` | 列出到期卡片（含 `overdue_days`） | `--deck`, `--limit` |
| `review undo` | 撤销 | — |

## search — 搜索

| 命令 | 说明 | 关键参数 |
|------|------|----------|
| `search cards "<query>"` | 搜索卡片 | `--limit`, `--order` |
| `search notes "<query>"` | 搜索笔记 | `--limit` |
| `search empty-cards` | 查找空卡片 | — |
| `search build "<parts>"` | 构建搜索串 | `--joiner` |

## tag — 标签管理

| 命令 | 说明 |
|------|------|
| `tag list` | 列出所有标签 |
| `tag tree` | 树形展示 |
| `tag add "<note_ids>" --tags "<tags>"` | 添加标签 |
| `tag remove "<note_ids>" --tags "<tags>"` | 移除标签 |
| `tag rename "<old>" "<new>"` | 重命名 |
| `tag delete "<tag>"` | 删除 |
| `tag clear-unused` | 清理未使用 |

## notetype — 笔记类型管理

| 命令 | 说明 |
|------|------|
| `notetype list` | 列出（含使用数） |
| `notetype info "<name>"` | 详情 |
| `notetype create "<name>"` | 创建 |
| `notetype copy "<name>" "<new>"` | 复制 |
| `notetype delete "<name>"` | 删除 |
| `notetype add-field "<type>" "<field>"` | 添加字段 |
| `notetype remove-field "<type>" "<field>"` | 移除字段 |
| `notetype rename-field "<type>" "<old>" "<new>"` | 重命名字段 |
| `notetype fields "<name>"` | 列出字段 |

## import — 导入

| 命令 | 说明 |
|------|------|
| `import apkg "<file>"` | 导入 .apkg |
| `import colpkg "<file>"` | 导入 .colpkg（替换集合） |
| `import csv "<file>" --deck "<d>" --type "<t>"` | 导入 CSV |
| `import json "<file>" --deck "<d>" --type "<t>"` | 导入 JSON |
| `import csv-preview "<file>"` | 预览 CSV 元数据 |

## export — 导出

| 命令 | 说明 |
|------|------|
| `export apkg --deck "<d>" --output "<f>"` | 导出 .apkg |
| `export colpkg --output "<f>"` | 导出 .colpkg |
| `export notes-csv --output "<f>"` | 笔记 CSV |
| `export cards-csv --output "<f>"` | 卡片 CSV |
| `export dataset` | FSRS 训练数据集 |

## sync — 同步

| 命令 | 说明 |
|------|------|
| `sync login --user "<u>" --password "<p>"` | 登录 AnkiWeb |
| `sync collection` | 同步集合 |
| `sync media` | 同步媒体 |
| `sync status` | 同步状态 |
| `sync full-upload` | 全量上传 |
| `sync full-download` | 全量下载 |

## stats — 统计

| 命令 | 说明 |
|------|------|
| `stats today` | 今日统计（studied_today） |
| `stats card <id>` | 单卡统计 |
| `stats deck` | 牌组 due 概览 |
| `stats memory <id>` | FSRS 记忆状态 |
| `stats overview` | 全局概览 |

## media / config / db / scheduler

| 命令 | 说明 |
|------|------|
| `media check` | 媒体完整性检查 |
| `media add "<file>"` | 添加媒体 |
| `config get "<key>"` | 获取配置 |
| `config set "<key>" "<val>"` | 设置配置 |
| `db check` | 数据库完整性检查修复 |
| `db optimize` | VACUUM + ANALYZE |
| `db backup` | 创建备份 |
| `db info` | 数据库信息 |
| `scheduler version` | 调度器版本 |
| `scheduler set-v3 --enable/--disable` | 启用/禁用 v3 |

## revlog — 复习日志查询

| 命令 | 说明 | 关键参数 |
|------|------|----------|
| `revlog query` | 按日期范围查询复习记录 | `--days N`, `--since`, `--until`, `--unique`, `--limit` |
| `revlog summary` | 复习活动汇总（次数、用时、评分分布） | `--days N`, `--since`, `--until`, `--group-by day\|card`, `--limit` |

## lang — 语言设置

| 命令 | 说明 |
|------|------|
| `lang set zh` | 设置界面为中文 |
| `lang set en` | 设置界面为英文 |
| `lang show` | 显示当前语言 |

## ac — AnkiConnect 模式（GUI 运行时）

| 命令 | 说明 |
|------|------|
| `ac decks` | 列出牌组 |
| `ac due` | 到期卡片 |
| `ac counts` | 今日复习数 |
| `ac search "<query>"` | 搜索 |
| `ac add --front "<f>" --back "<b>"` | 添加笔记 |
| `ac answer <card_id> --ease <1-4>` | 评分 |
| `ac suspend/unsuspend "<ids>"` | 暂停/恢复 |
| `ac tags` | 列出标签 |
| `ac add-tags "<note_ids>" --tags "<t>"` | 添加标签 |
| `ac notetypes` | 笔记类型 |
| `ac sync` | 触发同步 |
| `ac delete-notes "<ids>"` | 删除笔记 |
