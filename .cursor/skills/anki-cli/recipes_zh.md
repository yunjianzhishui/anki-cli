# anki-cli 高频配方速查表

> 10 个跨学科通用场景的完整命令序列。
> 每个配方可直接复制执行，AI 无需从头推导。
>
> 原子命令参考：[reference_zh.md](reference_zh.md) · 已知缺口：[known-gaps.md](known-gaps.md)

---

## RCP-01: 今日仪表盘

**用户说**："我今天该复习多少张卡片？来得及吗？"

```bash
anki-cli stats today --json
```

**关键字段**：

| 字段 | 含义 |
|------|------|
| `studied_today` | 今日已学 |
| `remaining_new` | 剩余新卡 |
| `remaining_learning` | 学习中 |
| `remaining_review` | 待复习 |
| `remaining_total` | 剩余总量 |

**进阶**：按牌组查看分布

```bash
anki-cli stats deck --json
# → [{deck, new, learn, review, total_due}, ...]
```

---

## RCP-02: 积压分诊

**用户说**："我好几天没复习了，积压了好多，帮我看看哪些最紧急？"

```bash
anki-cli review due --json
# → [{card_id, front, deck, due, interval, overdue_days}, ...]
```

**关键字段**：

| 字段 | 含义 |
|------|------|
| `overdue_days` | 逾期天数（正数=逾期，0=今天到期） |
| `interval` | 当前间隔（天） |

AI 按 `overdue_days` 降序排列即可找到最紧急的卡片。

**进阶**：只看特定牌组的积压

```bash
anki-cli review due --deck "高等数学" --json
```

---

## RCP-03: 时间 ROI / 水蛭猎杀

**用户说**："这个月花在背单词上的时间值不值？哪些卡片在浪费我的时间？"

**第一步**：月度概览

```bash
anki-cli revlog summary --days 30 --json
# → {total_reviews, unique_cards, total_time, again, hard, good, easy, learn, review, relearn}
```

**第二步**：找水蛭卡片（Anki 自动对反复失败的卡打 `leech` 标签）

```bash
anki-cli search cards "tag:leech -is:suspended" --json
# → {total, showing, cards: [{card_id, fields, lapses, reps, ...}]}
```

**第三步**：找耗时最多的卡片（Top 10）

```bash
anki-cli revlog summary --days 30 --group-by card --limit 10 --json
# → [{card_id, total_time_ms, review_count, again_count}, ...]
```

**关键字段**：

| 字段 | 含义 |
|------|------|
| `card_id` | 卡片 ID |
| `total_time_ms` | 累计用时（毫秒） |
| `review_count` | 复习次数 |
| `again_count` | 按 Again 的次数 |

**第四步（可选）**：查看耗时卡片的内容

```bash
anki-cli card info-batch "111,222,333" --json
```

---

## RCP-04: 从笔记批量建卡

**用户说**："我刚学完第三章的笔记，帮我把这些知识点做成卡片加进去。"

**第一步**：确认目标笔记类型的字段

```bash
anki-cli notetype list --json
anki-cli notetype fields "Basic" --json
```

**第二步**：逐张添加

```bash
anki-cli note add --deck "高等数学" --type "Basic" \
  --fields '{"Front":"什么是泰勒展开？","Back":"将函数在某点展开为幂级数的方法"}' \
  --tags "第三章,微积分"
```

**第三步（批量）**：AI 生成 JSON 文件后一次导入

```bash
anki-cli note add-batch --file cards.json --deck "高等数学" --type "Basic"
```

`cards.json` 格式：

```json
[
  {"fields": {"Front": "...", "Back": "..."}, "tags": ["第三章"]},
  {"fields": {"Front": "...", "Back": "..."}, "tags": ["第三章"]}
]
```

---

## RCP-05: 按标签查学习进度

**用户说**："帮我查一下，'民法总则'标签下的卡片，哪些是新卡还没学过？"

```bash
# 该标签下的新卡（未学过）
anki-cli search cards "tag:民法总则 is:new" --json
# → {total: 42, cards: [...]}

# 该标签下的全部卡片（对比用）
anki-cli search cards "tag:民法总则" --json
# → {total: 150, cards: [...]}
```

**关键字段（search cards 条目）**：

| 字段 | 含义 |
|------|------|
| `card_id` | 卡片 ID |
| `fields` | 字段名 → 内容 |
| `tags` | 标签列表 |
| `queue` | 队列状态 |
| `type` | 卡片类型（0=新, 1=学习, 2=复习） |
| `reps` | 复习次数 |
| `lapses` | 遗忘次数 |

**进阶**：查看已暂停的

```bash
anki-cli search cards "tag:民法总则 is:suspended" --json
```

---

## RCP-06: 批量暂停 / 恢复

**用户说**："把关于药理学的卡片暂停掉，期末考完再恢复。"

**暂停**：

```bash
# 先搜索获取 ID
anki-cli search cards "deck:药理学 -is:suspended" --json
# → 确认后提取 card_id 列表

# 批量暂停
anki-cli card suspend "111,222,333,444"
```

**恢复**（考完后）：

```bash
anki-cli search cards "deck:药理学 is:suspended" --json
anki-cli card unsuspend "111,222,333,444"
```

**进阶**：只暂停某个标签下的

```bash
anki-cli search cards "deck:药理学 tag:第五章 -is:suspended" --json
```

---

## RCP-07: 误操作修正

**用户说**："我昨天复习的时候，有几张卡按错了，点成 Easy 的其实没掌握，能撤回吗？"

**第一步**：查看昨天的复习记录

```bash
anki-cli revlog query --days 1 --json
# → {entries: [{card_id, time, rating, ...}]}
# AI 筛选 rating=="Easy" 的条目，展示给用户确认
```

精确到日期范围：

```bash
anki-cli revlog query --since 2026-03-09 --until 2026-03-09 --json
```

**第二步**：用户确认后修正

```bash
# 方案 A：设为今天到期，重新复习
anki-cli card set-due "111,222" --days 0

# 方案 B：彻底重置为新卡
anki-cli card forget "111,222"
```

**关键字段（revlog query 条目）**：

| 字段 | 含义 |
|------|------|
| `card_id` | 卡片 ID |
| `time` | 复习时间 |
| `rating` | Again / Hard / Good / Easy |
| `interval` | 新间隔 |
| `last_interval` | 上次间隔 |

---

## RCP-08: 跨牌组去重

**用户说**："我有两个英语牌组内容重复了，帮我找出重复的卡片。"

**第一步**：查找重复

```bash
anki-cli note duplicates --field "Front" --query "deck:英语词汇A OR deck:英语词汇B" --json
```

**第二步**：用户确认后清理

```bash
# 删除重复笔记
anki-cli note delete "111,222"

# 或者合并到一个牌组
anki-cli card move "111,222" --deck "英语词汇A"
```

---

## RCP-09: 正确率趋势

**用户说**："帮我看看我最近一周复习的正确率趋势，是在进步还是退步？"

```bash
anki-cli revlog summary --days 7 --group-by day --json
# → [{date, total, time_secs, again, hard, good, easy}, ...]
```

**关键字段**：

| 字段 | 含义 |
|------|------|
| `date` | 日期（YYYY-MM-DD） |
| `total` | 当天复习总次数 |
| `again` / `hard` / `good` / `easy` | 各评分次数 |
| `time_secs` | 当天用时（秒） |

AI 直接计算每天 `correct_rate = (good + easy) / total`，即可得出趋势。

---

## RCP-10: 延后简单卡

**用户说**："这些卡片太简单了，我想让它们间隔长一点，别老出现。"

**第一步**：找出"太简单"的卡片

```bash
# 过去 7 天全按 Easy、且间隔仍然短（<30天）的卡片
anki-cli search cards "rated:7:4 prop:ivl<30" --json
# → {cards: [{card_id, fields, interval, ease_factor, reps, ...}]}
```

**第二步**：延后到期日

```bash
anki-cli card set-due "111,222,333" --days 60
```

**备选方案**：直接暂停

```bash
anki-cli card suspend "111,222,333"
```

**常用搜索语法补充**：

| 语法 | 含义 |
|------|------|
| `rated:N:E` | 过去 N 天内按 E 评分（1=Again, 4=Easy） |
| `prop:ivl<30` | 间隔小于 30 天 |
| `prop:ease<2.0` | 难度系数低于 2.0（"Ease Hell"） |
| `prop:lapses>5` | 遗忘超过 5 次 |
