---
name: v2ex
description: |
  V2EX 社区搜索助手。通过 Python 命令搜索 V2EX：搜索主题、查看主题详情与回复、浏览热门/最新主题、查看节点信息、查看用户资料。
  当用户提到 V2EX、v2ex、V 站、v 站、V2EX 搜索、V2EX 帖子等关键词时使用。
---

# 规则

1. **只用下面的 python3 命令。禁止用 curl、wget、httpie 或任何其他方式。**
2. 首次使用先运行初始化：`cd ~/.openclaw/skills/v2ex && bash scripts/setup.sh`
3. V2EX API 有频率限制，请勿频繁请求

# 命令

以下是全部可用命令，`P` 代表 `python3 ~/.openclaw/skills/v2ex/scripts/v2ex_client.py`。

## 无需登录

| 功能 | 命令 |
|------|------|
| 搜索主题 | `P search "关键词"` |
| 主题详情 | `P topic <topic_id>` |
| 主题回复 | `P replies <topic_id>` |
| 热门主题 | `P hot` |
| 最新主题 | `P latest` |
| 节点信息 | `P node <node_name>` |
| 节点主题 | `P node-topics <node_name>` |
| 用户资料 | `P user <username>` |
| 用户主题 | `P user-topics <username>` |

## 需要 Token（V2EX API v2）

| 功能 | 命令 |
|------|------|
| 导入 Token | `P import-token` |

# Token 导入

部分高级功能需要 V2EX Personal Access Token：

1. 登录 v2ex.com，进入 设置 → Tokens
2. 创建新 Token
3. 保存到 `~/.openclaw/skills/v2ex/token.txt`

# 示例

```shell
# 搜索主题
python3 ~/.openclaw/skills/v2ex/scripts/v2ex_client.py search "Python 异步"

# 查看主题详情
python3 ~/.openclaw/skills/v2ex/scripts/v2ex_client.py topic 12345

# 查看热门主题
python3 ~/.openclaw/skills/v2ex/scripts/v2ex_client.py hot

# 查看节点主题
python3 ~/.openclaw/skills/v2ex/scripts/v2ex_client.py node-topics python
```
