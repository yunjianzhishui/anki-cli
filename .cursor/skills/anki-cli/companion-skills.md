# anki-cli 配套 Skills 指南

> anki-cli 不仅是命令行工具，也是 AI 教学 Skill 的基础设施。
> 本文档介绍随 anki-cli 一起发布的配套练习 Skills，帮助用户快速搭建 Anki 驱动的教学环境。

## 概览

anki-cli 仓库内置以下 Skills：

| Skill | 路径 | 用途 |
|-------|------|------|
| **anki-cli** | `.cursor/skills/anki-cli/` | 核心 Skill：Anki 命令行操作专家 |
| **anki-report** | `.cursor/skills/anki-report/` | 报告分析：生成日报/周报/月报，七大维度洞察建议 |
| **wenyan-translator** | `.cursor/skills/wenyan-translator/` | 文言文翻译教学（脚手架教学法 + Anki 驱动） |
| **shanghai-english-translator** | `.cursor/skills/shanghai-english-translator/` | 上海高考英语翻译教学（命题人视角 + Anki 驱动） |

### 架构关系

```
anki-cli (核心工具层)
  ├── anki-cli skill        (操作专家，知道所有命令)
  ├── anki-report skill     (报告层，聚合数据 → 分析 → Markdown 报告)
  ├── wenyan-translator skill          (教学层，调用 anki-cli 命令)
  └── shanghai-english-translator skill (教学层，调用 anki-cli 命令)
```

教学 Skills 是 anki-cli 的**上层应用**：它们定义教学工作流，在需要操作 Anki 数据时调用 anki-cli 命令。anki-report Skill 是**分析层**：通过 `collect_data.py` 一次性收集数据，由 AI 生成报告。教学 Skills 可在练习结束后调用 anki-report 生成日报。

## 快速开始

### 1. 安装 anki-cli

```bash
cd anki-cli
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e .
anki-cli --version
```

### 2. 确认你的牌组

```bash
anki-cli deck list
```

记下你要用的牌组名（如 `高中文言300`、`高考英语` 等）。

### 3. 在 Cursor 中启用

用 Cursor 打开 anki-cli 仓库根目录，所有 Skills 自动加载。

如果 anki-cli 是你项目的子文件夹，请将 `.cursor/skills/` 下需要的 Skill 文件夹复制到你的项目的 `.cursor/skills/` 中。

### 4. 开始练习

在 Cursor 对话中说：

| 你说的话 | 触发的 Skill |
|---------|-------------|
| "列出牌组" / "查卡片" / "复习统计" | anki-cli（操作专家） |
| "生成日报" / "生成周报" / "卡包体检" | anki-report（报告分析） |
| "文言文翻译练习" / "复习文言文" | wenyan-translator（文言文教学） |
| "出英语题" / "英语翻译练习" / "上海高考翻译" | shanghai-english-translator（英语教学） |

## 各 Skill 详细说明

### anki-cli — Anki 操作专家

**角色**：知道 anki-cli 的全部命令，帮你或其他 Skill 执行 Anki 数据操作。

**核心能力**：
- 列出牌组、搜索卡片、查看统计
- 复习流程（拉取待复习卡片、提交评分）
- 添加/编辑/删除笔记
- 导入导出、同步

**详细文档**：
- 英文：[SKILL.md](SKILL.md) · [reference.md](reference.md) · [recipes.md](recipes.md)
- 中文：[SKILL_zh.md](SKILL_zh.md) · [reference_zh.md](reference_zh.md) · [recipes_zh.md](recipes_zh.md)

---

### anki-report — Anki 学习报告分析

**角色**：学习数据分析师，生成日报/周报/月报，从七大维度提供洞察和建议。

**工作流**：
1. 运行 `collect_data.py --scope <daily|weekly|monthly> --profile "<name>"`
2. 脚本一次性调用多个 anki-cli 命令，输出完整 JSON
3. AI 解析 JSON，按模板生成 Markdown 报告
4. 保存到 `reports/daily|weekly|monthly/`

**七大分析维度**：
- 学习量与规律性（连续天数、日均复习量）
- 记忆质量（正确率、Again/Hard/Good/Easy 分布）
- 积压与负债（到期、新卡、挂起卡片队列）
- 难点热力图（频繁 Again 的水蛭卡片）
- 时间效率（每卡平均耗时、高耗时卡片）
- 卡包结构健康度（总卡片/牌组分布）
- 学科交叉分析（周报/月报，读取练习记录）

**触发词**：生成日报、生成周报、生成月报、学习报告、卡包分析、卡包体检

**详细文档**：[../anki-report/SKILL.md](../anki-report/SKILL.md)

---

### wenyan-translator — 文言文翻译教学

**角色**：文言文翻译教练，基于脚手架教学法。

**Anki 驱动全流程**：
1. `anki-cli review due` — 拉取待复习的文言实词卡片
2. AI 将实词融入一篇文言文（主题随机，实词加粗）
3. 用户口述翻译 → AI 启发式诊断（5 分制）
4. `anki-cli review answer-batch` — 四档差异化写回
5. 生成练习记录
6. `anki-cli note add` — 可选补充知识卡片

**教学特色**：
- 严禁直接给答案，通过引导让学生推导
- 四维归因分析（ERR-A 实词 / ERR-B 语法 / ERR-C 技巧 / ERR-D 常识）
- 变式强化（满分后出同类型变式题）

**详细文档**：[../wenyan-translator/SKILL.md](../wenyan-translator/SKILL.md)

---

### shanghai-english-translator — 上海高考英语翻译教学

**角色**：上海高考英语命题人，按高考格式出翻译题。

**Anki 驱动全流程**：
1. `anki-cli review due` — 拉取待复习的英语词汇卡片
2. AI 按高考格式出题：`中文句子。(English word)`
3. 用户作答 → AI 按高考标准诊断
4. `anki-cli review answer-batch` — 四档差异化写回
5. 生成练习记录
6. `anki-cli note add` — 可选补充知识卡片

**题目格式**：
- 中译英：`这块布料轻薄又速干，最适合做运动装。(cloth)`
- 英译中：`The substantial increase in revenue... (大量的)`

**详细文档**：[../shanghai-english-translator/SKILL.md](../shanghai-english-translator/SKILL.md)

## 自定义与扩展

### 创建你自己的教学 Skill

任何学科都可以参考 wenyan-translator 和 shanghai-english-translator 的模式，创建自己的 Anki 驱动教学 Skill。核心模式为：

1. **拉取**：`anki-cli review due --deck "<deck>" --limit N --json`
2. **出题**：AI 根据卡片内容生成练习题
3. **诊断**：用户作答后 AI 评估
4. **写回**：`anki-cli review answer-batch --data '[...]'`
5. **补卡**：`anki-cli note add --deck "<deck>" --type "..." --fields '{...}'`

### 适用学科示例

| 学科 | 拉取的卡片 | 练习形式 |
|------|-----------|---------|
| 文言文 | 实词卡片 | 生成含实词的文言文 → 翻译 |
| 英语 | 词汇卡片 | 高考格式翻译题 |
| 化学 | 方程式卡片 | 配平/预测产物 |
| 历史 | 事件卡片 | 时间线/因果分析 |
| 生物 | 概念卡片 | 填空/概念辨析 |
| 数学 | 公式卡片 | 应用题 |

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| "command not found: anki-cli" | 运行 `pip install -e .`；确认虚拟环境已激活 |
| "Collection is already open" | 关闭 Anki 桌面版，或使用 `anki-cli ac` 前缀（AnkiConnect 模式） |
| 找不到牌组 | 运行 `anki-cli deck list` 确认牌组名，注意大小写 |
| Skill 不触发 | 确认 `.cursor/skills/` 下有对应文件夹；重新打开 Cursor 工作区 |
| 写回评分失败 | 确认 card_id 有效：`anki-cli card info <card_id>` |
