---
name: v2ex-topic
description: |
  查看 V2EX 主题详情、回复、热门主题、最新主题。当用户想了解某个 V2EX 帖子的内容、回复，或浏览热门/最新帖子时使用。
---

# 规则

**只用下面的 python3 命令，禁止使用 curl 或其他方式。**

`P` 代表 `python3 <SKILL_DIR>/scripts/v2ex_client.py`（SKILL_DIR：`~/.claude/skills/v2ex` 或 `~/.openclaw/skills/v2ex`，取存在的路径）。

# 命令

| 功能 | 命令 |
|------|------|
| 主题详情 | `P topic <topic_id>` |
| 主题回复 | `P replies <topic_id>` |
| 热门主题 | `P hot` |
| 最新主题 | `P latest` |

# 展示格式

主题详情展示：标题、作者、节点、回复数、发布时间、正文内容。回复展示：序号、用户名、时间、内容。
