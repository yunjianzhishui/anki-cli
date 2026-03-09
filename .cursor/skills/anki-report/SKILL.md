---
name: anki-report
description: >-
  Anki 报告分析大师。通过 anki-cli 收集学习数据，生成日报/周报/月报 Markdown 报告，
  并基于七大维度提供卡包内容、结构和学习习惯的优化建议。
  可被其他 skill 在练习结束后调用生成报告。
  触发词：生成日报、生成周报、生成月报、学习报告、卡包分析、卡包体检、Anki report。
metadata:
  version: 1.1.0
  priority: 1
---

# Anki 报告分析大师

通过组合 anki-cli 积木收集学习数据，从七大维度进行分析，生成 Markdown 报告，并给出可操作的优化建议。

> **此版本适用于：将 anki-cli 仓库作为 workspace root 直接打开的场景。**
> 若 anki-cli 是外部项目的子文件夹，请使用外部项目 `.cursor/skills/anki-report/` 下的版本。

## 适用场景

- 每日练习后快速回顾（日报）
- 每周学习复盘与趋势分析（周报）
- 月度卡包健康体检与战略调整（月报）
- 卡包结构审查与优化
- 跨学科学习分配分析

## 依赖

- **anki-cli skill**：复用 anki-cli 命令执行约定（profile、连接模式、执行路径）
- **anki-cli 执行方式**：`.venv/Scripts/python.exe -m ankicli --profile "<name>" --json <cmd>`

## 工作流程

### Core Logic: 意图判定

接收用户输入后，判定报告类型：

1. **日报**：用户提到「生成日报」「今日报告」「daily report」等
2. **周报**：用户提到「生成周报」「本周报告」「weekly report」等
3. **月报**：用户提到「生成月报」「月度报告」「卡包体检」「monthly report」等
4. **快速分析**：用户提到「卡包分析」「学习报告」等 → 默认生成日报

### Step 1: 数据收集

在 anki-cli 仓库根目录下运行数据收集脚本：

```bash
.venv/Scripts/python.exe .cursor/skills/anki-report/scripts/collect_data.py --scope <daily|weekly|monthly> --profile "<name>"
```

示例（profile 为"操东瀚"）：

```bash
.venv/Scripts/python.exe ".cursor/skills/anki-report/scripts/collect_data.py" --scope daily --profile "操东瀚"
```

脚本输出一个完整的 JSON 到 stdout，包含所有原始数据和派生指标。

### Step 2: 解析 JSON 并生成报告

解析 collect_data.py 的 JSON 输出，按报告类型选择对应模板生成 Markdown。

### Step 3: 运行洞察引擎

基于数据触发下方「洞察引擎」中的规则，生成个性化建议。

### Step 4: 保存报告

报告保存路径（相对于 workspace root，即 anki-cli 目录）：

| 报告类型 | 路径 | 文件名 |
|----------|------|--------|
| 日报 | `reports/daily/` | `日报-YYYY-MM-DD.md` |
| 周报 | `reports/weekly/` | `周报-YYYY-Wxx.md` |
| 月报 | `reports/monthly/` | `月报-YYYY-MM.md` |

> **注**：若用户指定了其他保存路径，以用户指定的为准。

---

## 七大分析维度

### 1. 学习量与规律性

| 指标 | 数据源 | 日报 | 周报 | 月报 |
|------|--------|------|------|------|
| 复习卡片总数 | revlog_summary.total_reviews | 展示 | 日均+总计 | 周均+总计 |
| 学习时长 | revlog_summary.total_time | 展示 | 日均+总计 | 周均+总计 |
| 连续学习天数 | study_streak_days | 展示 | 展示 | 趋势 |
| 日复习量分布 | daily_breakdown | -- | 7 天表格 | 30 天趋势 |

**阈值**：
- study_streak < 3 天 → 标记为「规律性不足」
- 日复习量标准差 > 均值 × 0.5 → 标记为「波动较大」

### 2. 记忆质量

| 指标 | 数据源 | 日报 | 周报 | 月报 |
|------|--------|------|------|------|
| 正确率 | retention_rate | 百分比 | 趋势 | 曲线 |
| Ease 分布 | revlog_summary (again/hard/good/easy) | 四档计数 | 日趋势 | 周趋势 |
| 遗忘比 | again / total | 百分比 | 趋势 | 趋势 |

**阈值**：
- retention_rate < 0.70 → 「记忆质量偏低」
- again 占比 > 0.20 → 「遗忘率偏高」

### 3. 积压与负债

| 指标 | 数据源 | 日报 | 周报 | 月报 |
|------|--------|------|------|------|
| 到期卡片数 | queue_depth.overdue | 快照 | 趋势 | 趋势 |
| 新卡队列深度 | queue_depth.new | 快照 | 趋势 | 预测 |
| 挂起卡片数 | queue_depth.suspended | 快照 | 占比 | 审查建议 |
| 各牌组到期分布 | deck_overview | -- | 表格 | 表格+建议 |

**阈值**：
- overdue > 50 → 「积压严重，建议暂停新卡」
- new > 200 → 「新卡积压，建议分批引入」
- suspended / total_cards > 0.20 → 「挂起卡片过多，建议审查」

### 4. 难点热力图

| 指标 | 数据源 | 日报 | 周报 | 月报 |
|------|--------|------|------|------|
| 频繁 Again 的卡片 | difficulty_hotspots | Top-5 | Top-10 | Top-20 + 分析 |
| 各牌组难度排行 | 按牌组聚合 again 比例 | -- | 排行 | 排行+建议 |

**阈值**：
- 同一张卡 Again >= 3 次（周内）→ 标记为「水蛭卡片」，建议拆分或添加助记

### 5. 时间效率

| 指标 | 数据源 | 日报 | 周报 | 月报 |
|------|--------|------|------|------|
| 每卡平均时间 | avg_time_per_card_sec | 展示 | 趋势 | 趋势 |
| 高耗时卡片 | time_hotspots | Top-3 | Top-5 | Top-10 |

**阈值**：
- avg_time > 30 秒 → 「卡片可能内容过长，建议拆分」
- 单卡 > 60 秒 → 标记为高耗时卡片

### 6. 卡包结构健康度

| 指标 | 数据源 | 日报 | 周报 | 月报 |
|------|--------|------|------|------|
| 总卡片/笔记/牌组数 | global_overview | -- | 快照 | 快照 |
| 各牌组卡片分布 | deck_overview | -- | -- | 表格 |
| 新/学习/复习比例 | deck_overview 汇总 | -- | 饼图描述 | 详细分析 |

### 7. 学科交叉分析（周报/月报）

从练习记录文件读取归因数据：

| 指标 | 数据源 | 周报 | 月报 |
|------|--------|------|------|
| 各学科练习次数 | 练习记录文件计数 | 统计 | 统计+趋势 |
| 归因维度分布 | 练习记录中的 ERR-A/B/C/D | -- | 四维分布 |
| 学科时间分配 | 练习记录 | -- | 建议 |

---

## 洞察引擎（建议规则）

AI 基于以下规则，在报告末尾给出「洞察与建议」：

### 卡片内容优化

| 条件 | 建议 |
|------|------|
| difficulty_hotspots 中某卡 Again >= 3（周内） | 这张卡是「水蛭卡片」，建议：拆分为更小知识点、添加助记线索（谐音/画面/关联）、或改用 Cloze 填空格式 |
| time_hotspots 中某卡 > 60 秒 | 卡片内容过长，建议拆分为多张原子卡片（最小信息原则） |
| 有 empty cards（可调用 `search empty-cards`） | 有空卡片需要清理，运行 `search empty-cards` 查看 |

### 卡包结构优化

| 条件 | 建议 |
|------|------|
| queue_depth.new > 200 | 新卡积压过多（{N} 张），建议适当提高每日新卡引入数或分批学习 |
| queue_depth.overdue > 50 | 到期卡片积压严重（{N} 张），建议暂停新卡引入，优先清理积压 |
| queue_depth.suspended / total > 0.20 | 挂起卡片占比过高（{pct}%），建议审查挂起卡片，决定复用或删除 |
| 某牌组 total_due = 0 且卡片数 > 0（连续 7 天） | 该牌组可能已废弃，建议归档或合并到活跃牌组 |

### 学习习惯优化

| 条件 | 建议 |
|------|------|
| study_streak_days < 3 | 连续学习仅 {N} 天，建议设置固定复习时间，哪怕每天只做 10 张 |
| 日复习量标准差 / 均值 > 0.5 | 学习量波动较大，存在「暴食式学习」倾向，建议控制每日上限，保持匀速 |
| retention_rate < 0.70 | 正确率偏低（{pct}%），建议暂时降低每日新卡数，先巩固已学内容 |
| retention_rate > 0.95 且 overdue = 0 | 正确率极高，当前节奏很好！可考虑适当增加新卡引入 |
| again 占比 > 0.20 | 遗忘率偏高（{pct}%），可能学习间隔过长或一次引入太多新卡 |

---

## 报告模板

### 日报模板

```markdown
# Anki 日报 · {YYYY-MM-DD} · {profile}

## 今日概览

| 指标 | 值 |
|------|-----|
| 复习卡片数 | {studied_today} |
| 正确率 (Good+Easy) | {retention_rate}% |
| 学习时长 | {total_time} |
| 连续学习天数 | {streak} 天 |

## Ease 分布

| Again | Hard | Good | Easy |
|-------|------|------|------|
| {again} | {hard} | {good} | {easy} |

## 待办队列

| 到期 | 新卡 | 挂起 |
|------|------|------|
| {overdue} | {new} | {suspended} |

## 今日难点

{difficulty_hotspots 列表，每张卡显示 card_id 和所属牌组}

## 洞察与建议

{根据洞察引擎规则生成的建议列表}
```

### 周报模板

在日报基础上增加：

```markdown
## 7 天趋势

| 日期 | 复习数 | Again | Hard | Good | Easy | 正确率 | 时长 |
|------|--------|-------|------|------|------|--------|------|
| {逐日数据} |

## 本周 vs 上周

| 指标 | 本周 | 上周 | 变化 |
|------|------|------|------|
| 总复习数 | | | |
| 平均正确率 | | | |
| 平均每日时长 | | | |

## 各牌组分析

| 牌组 | 新卡 | 学习中 | 复习 | 到期合计 |
|------|------|--------|------|----------|
| {deck_overview 数据} |

## 难点 Top-10

{difficulty_hotspots 前 10 张，含 Again 次数}

## 卡包健康度

| 指标 | 值 | 状态 |
|------|-----|------|
| 总卡片数 | {total_cards} | — |
| 积压率 | {overdue/total}% | {正常/警告/严重} |
| 挂起率 | {suspended/total}% | {正常/偏高} |
| 新卡深度 | {new} | {正常/积压} |
```

### 月报模板

在周报基础上增加：

```markdown
## 30 天趋势

{按周汇总的复习量、正确率、时长表格}

## 卡包全面体检

| 检查项 | 结果 | 建议 |
|--------|------|------|
| 水蛭卡片（Again>=5） | {count} 张 | {建议} |
| 高耗时卡片（>60s） | {count} 张 | {建议} |
| 挂起卡片 | {count} 张 | {建议} |
| 空卡片 | {count} 张 | {建议} |
| 新卡积压 | {count} 张 | {建议} |

## 学科交叉分析

| 学科 | 练习次数 | 薄弱维度 |
|------|----------|----------|
| 文言文 | {count} | {ERR-A/B/C/D 分布} |
| 英语 | {count} | — |

## 战略建议

{基于月度数据的长期优化建议}
```

---

## 供其他 Skill 调用

其他 skill（如 wenyan-translator、shanghai-english-translator 等）可在练习结束后调用本 skill 生成日报。调用方式：

1. 读取本 SKILL.md 获取执行方式
2. 在 anki-cli 仓库根目录运行 `collect_data.py --scope daily --profile "<name>"`
3. 解析 JSON，按日报模板生成报告
4. 保存到 `reports/daily/`

## 相关 Skills

- **anki-cli**：`.cursor/skills/anki-cli/SKILL.md`（anki-cli 命令执行约定）
- **wenyan-translator**：`.cursor/skills/wenyan-translator/SKILL.md`（练习记录用于学科交叉分析）
- **shanghai-english-translator**：`.cursor/skills/shanghai-english-translator/SKILL.md`（练习记录用于学科交叉分析）
