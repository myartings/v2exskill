---
name: v2ex-node
description: |
  查看 V2EX 节点信息和节点下的主题。当用户想了解某个 V2EX 节点（如 python、golang、程序员等）的信息或浏览节点主题时使用。
---

# 规则

**只用下面的 python3 命令，禁止使用 curl 或其他方式。**

`P` 代表 `python3 ~/.openclaw/skills/v2ex/scripts/v2ex_client.py`。

# 命令

| 功能 | 命令 |
|------|------|
| 节点信息 | `P node <node_name>` |
| 节点主题 | `P node-topics <node_name>` |

# 常用节点

python, golang, java, nodejs, programmer, apple, create, jobs, qna, share, macos, linux, career

# 展示格式

节点信息展示：名称、别名、主题数、关注数、描述。节点主题展示：标题、作者、回复数、时间。
