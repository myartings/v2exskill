# V2EX Skill

V2EX OpenClaw Skill。

## 架构

- 纯 Python 3 标准库，无第三方依赖
- 搜索使用 SOV2EX API（`www.sov2ex.com`）+ DuckDuckGo 双通道
- 主题/节点/用户使用 V2EX 官方 API v1（无需认证）
- 部分功能支持 V2EX API v2（需 Personal Access Token）
- CLI 客户端：`scripts/v2ex_client.py`

## 项目结构

```
├── SKILL.md                         # OpenClaw 根 skill
├── CLAUDE.md                        # 架构文档（本文件）
├── skills/                          # 4 个子 skill
│   ├── v2ex-search/SKILL.md
│   ├── v2ex-topic/SKILL.md
│   ├── v2ex-node/SKILL.md
│   └── v2ex-user/SKILL.md
├── scripts/v2ex_client.py           # V2EX 客户端
├── scripts/setup.sh                 # 初始化脚本
```

## V2EX API 说明

- V2EX API v1（公开）：`https://www.v2ex.com/api/`
  - 无需认证，有频率限制
  - 主题、节点、用户信息
- V2EX API v2：`https://www.v2ex.com/api/v2/`
  - 需要 Personal Access Token
  - 更丰富的数据
- SOV2EX 搜索：`https://www.sov2ex.com/api/hit/web/post/`
  - 第三方全文搜索引擎
  - 无需认证

## 数据来源

| 功能 | 数据来源 | 需要 Token |
|------|----------|------------|
| search | SOV2EX API / DuckDuckGo | 否 |
| topic | V2EX API v1 | 否 |
| replies | V2EX API v1 | 否 |
| hot | V2EX API v1 | 否 |
| latest | V2EX API v1 | 否 |
| node | V2EX API v1 | 否 |
| node-topics | V2EX API v1 | 否 |
| user | V2EX API v1 | 否 |
| user-topics | V2EX API v1 | 否 |

## 添加新功能

1. 在 `v2ex_client.py` 中添加 `cmd_xxx()` 函数
2. 在 `main()` 的 `commands` 字典中注册
3. 更新 `SKILL.md` 命令表
4. 如需新的子 skill，在 `skills/` 下创建目录和 `SKILL.md`
5. 测试：`python3 scripts/v2ex_client.py xxx <args>`
