---
name: v2ex-user
description: |
  查看 V2EX 用户资料和用户发布的主题。当用户想了解某个 V2EX 用户的信息时使用。
---

# 规则

**只用下面的 python3 命令，禁止使用 curl 或其他方式。**

`P` 代表 `python3 <SKILL_DIR>/scripts/v2ex_client.py`（SKILL_DIR：`${CLAUDE_PLUGIN_ROOT}` 或 `~/.openclaw/skills/v2ex` 或 `~/.claude/skills/v2ex`，取存在的路径）。

# 命令

| 功能 | 命令 |
|------|------|
| 用户资料 | `P user <username>` |
| 用户主题 | `P user-topics <username>` |
| 导入 Token | `P import-token` |

# 展示格式

用户资料展示：用户名、签名、简介、位置、网站、GitHub、注册时间。用户主题展示：标题、节点、回复数、时间。
