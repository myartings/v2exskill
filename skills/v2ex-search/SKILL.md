---
name: v2ex-search
description: |
  搜索 V2EX 社区内容。当用户想搜索 V2EX 上的帖子、讨论时使用。
---

# 规则

**只用下面的 python3 命令，禁止使用 curl 或其他方式。**

`P` 代表 `python3 ~/.openclaw/skills/v2ex/scripts/v2ex_client.py`。

# 命令

| 功能 | 命令 |
|------|------|
| 搜索主题 | `P search "关键词"` |

# 展示格式

搜索结果包含主题标题、摘要、节点、作者、回复数。每条结果展示：标题、摘要、元信息、链接。默认展示 15 条。
