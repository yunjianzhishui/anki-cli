# anki-cli Skill 安装与注册指南

本 skill 让 AI 助手（如 Cursor）在对话中直接使用 anki-cli 执行 Anki 操作。根据你的 IDE 选择对应方式。

---

## Cursor（推荐）

### 方式一：直接打开本仓库（推荐）

1. 用 Cursor 打开 **anki-cli 仓库根目录**（File → Open Folder → 选择 anki-cli 文件夹）
2. 无需额外操作，Skill 自动加载（位于 `.cursor/skills/anki-cli/`）
3. 在对话中可直接说「查卡片」「列出牌组」「复习统计」等，AI 会调用 anki-cli

### 方式二：anki-cli 作为子目录

若你的工作区是父级目录（如 `my-project/`），anki-cli 在 `my-project/anki-cli/` 下：

1. 将 `anki-cli/.cursor/skills/anki-cli/` 复制到 `my-project/.cursor/skills/anki-cli/`
2. 确保 `my-project` 的 `.cursor/skills/` 目录存在
3. 重新打开 Cursor 或刷新工作区

### 验证

在 Cursor 对话中输入：`列出我的牌组` 或 `anki-cli deck list`，AI 应能执行并返回结果。

---

## 其他 IDE（VS Code、JetBrains 等）

本 skill 的格式为 **Cursor 专用**。其他 IDE 若使用 AI 助手（如 Copilot、Codeium、Cursor 插件等），可尝试：

1. **复制 SKILL_zh.md 内容**：将 `.cursor/skills/anki-cli/SKILL_zh.md` 的正文复制到你的 AI 助手的「自定义指令」「规则」或「系统提示」中
2. **作为参考文档**：将 `SKILL_zh.md` 和 `reference_zh.md` 作为项目文档，在需要时手动引用给 AI

不同 IDE 的 AI 集成方式各异，请查阅对应产品的文档。

---

## 语言切换

- **CLI**：首次运行会提示选择语言（中文/English）。之后可用 `anki-cli lang set zh` 或 `anki-cli lang set en` 切换。
- **Skill**：AI 根据用户消息语言自动选择 SKILL.md（英文）或 SKILL_zh.md（中文）。

---

## 前置条件

- 已执行 `pip install -e .` 安装 anki-cli
- Anki 桌面版已安装（若需日常刷卡片）
- 直接模式：Anki GUI 关闭；AnkiConnect 模式：GUI 运行中且已安装 AnkiConnect 插件（2055492159）
