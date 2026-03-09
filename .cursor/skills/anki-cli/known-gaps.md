# anki-cli 已知功能缺口（积木视角）

> **设计原则**：anki-cli 的每个命令应是一块可组合的积木，而非为特定场景定制的完整方案。
> 缺口分析应找出"缺哪块积木"，而非"缺哪个完整功能"。

---

## GAP-001: revlog 查询积木

**状态**: ✅ 已实现  
**实现**: `revlog query` + `revlog summary`，见 `ankicli/cmd_revlog.py`

```bash
anki-cli revlog query --days 1 --unique --json
anki-cli revlog summary --days 1
```

---

## GAP-002: card info 批量查询

**状态**: ✅ 已实现  
**实现**: `card info-batch`，见 `ankicli/cmd_card.py`

```bash
anki-cli card info-batch "111,222,333" --json
```

---

## GAP-003: review due 缺少 overdue_days 字段

**状态**: ✅ 已实现  
**实现**: `review due --json` 输出增加 `overdue_days` 字段，见 `ankicli/cmd_review.py`

```bash
anki-cli review due --json
# overdue_days: 正数=逾期天数, 0=今天到期, 负数=未到期
```

---

## GAP-004: revlog summary 缺少按卡片分组能力

**状态**: ✅ 已实现  
**实现**: `revlog summary --group-by card`，见 `ankicli/cmd_revlog.py`

```bash
anki-cli revlog summary --days 30 --group-by card --limit 10 --json
# → [{card_id, total_time_ms, review_count, again_count}, ...]
anki-cli card info-batch "111,222,333" --json   # (GAP-002)
# → 查看这些卡片的内容，决定是否暂停或重做
```

---

## GAP-005: revlog summary 缺少按天分组的趋势输出

**状态**: ✅ 已实现  
**实现**: `revlog summary --group-by day`，见 `ankicli/cmd_revlog.py`（与 GAP-004 合并为 `--group-by` 参数）

```bash
anki-cli revlog summary --days 7 --group-by day --json
# → [{date, total, time_secs, again, hard, good, easy}, ...]
```

---

<!--
添加新缺口模板:

## GAP-NNN: <缺失的积木名称>

**状态**: 未实现 / 已实现(版本)  
**发现日期**: YYYY-MM-DD  
**触发场景**: 什么组合操作做不到

**缺失分析**: 现有积木有哪些，缺哪一块导致组合断裂

**建议积木**: 最小化的原子命令设计（输入、输出、参数）

**组合示例**: 补上这块积木后，如何与已有命令组合完成目标
-->
