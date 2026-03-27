#!/usr/bin/env python3
"""V2EX CLI Client.

Usage:
    python v2ex_client.py search <keyword>          # Search topics
    python v2ex_client.py topic <topic_id>          # Topic detail
    python v2ex_client.py replies <topic_id>        # Topic replies
    python v2ex_client.py hot                       # Hot topics
    python v2ex_client.py latest                    # Latest topics
    python v2ex_client.py node <node_name>          # Node info
    python v2ex_client.py node-topics <node_name>   # Node topics
    python v2ex_client.py user <username>           # User profile
    python v2ex_client.py user-topics <username>    # User topics
    python v2ex_client.py import-token              # Import API token

Token: Reads from ~/.openclaw/skills/v2ex/token.txt (optional).
"""

import sys
import os
import json
import re
import html as html_module
import urllib.request
import urllib.error
import urllib.parse
import time

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.join(SKILL_DIR, "token.txt")

V2EX_API_V1 = "https://www.v2ex.com/api"
V2EX_API_V2 = "https://www.v2ex.com/api/v2"
SOV2EX_API = "https://www.sov2ex.com/api/hit/web/post"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.v2ex.com/",
}


# ── Token Management ──────────────────────────────────────────────────────

def get_token():
    """Read V2EX API token from file."""
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE) as f:
                token = f.read().strip()
            if token:
                return token
        except Exception:
            pass
    return None


# ── Network Layer ─────────────────────────────────────────────────────────

def fetch_json(url, headers=None, use_token=False):
    """Fetch a URL expecting JSON response."""
    hdrs = dict(HEADERS)
    if headers:
        hdrs.update(headers)
    if use_token:
        token = get_token()
        if token:
            hdrs["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        return json.loads(body)
    except urllib.error.HTTPError as e:
        code = e.code
        body = e.read().decode("utf-8", errors="replace")[:500]
        if code == 403:
            return {"error": "访问被限制 (403)，可能触发了频率限制，请稍后再试。"}
        if code == 404:
            return {"error": "资源不存在 (404)"}
        if code == 401:
            return {"error": "需要认证 (401)，请导入 Token"}
        return {"error": f"HTTP {code}: {body}"}
    except json.JSONDecodeError:
        return {"error": "非 JSON 响应"}
    except Exception as e:
        return {"error": str(e)}


def fetch_html(url, headers=None):
    """Fetch a URL and return the response body as string."""
    hdrs = dict(HEADERS)
    hdrs["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return json.dumps({"error": f"HTTP {e.code}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def strip_html(text):
    if not text:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html_module.unescape(text)
    return text.strip()


def truncate(text, length=200):
    text = text.replace("\n", " ").strip()
    if len(text) > length:
        return text[:length] + "..."
    return text


def check_error(r):
    if isinstance(r, dict) and "error" in r:
        print(f"错误: {r['error']}")
        return True
    return False


def format_time(ts):
    """Format a unix timestamp to readable string."""
    if not ts:
        return ""
    try:
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(int(ts)))
    except (ValueError, TypeError, OSError):
        return str(ts)


# ── Search via SOV2EX ─────────────────────────────────────────────────────

def _search_sov2ex(keyword, page=1, size=15):
    """Search V2EX topics via SOV2EX full-text search engine."""
    params = urllib.parse.urlencode({
        "q": keyword,
        "from": (page - 1) * size,
        "size": size,
        "sort": "sumup",
    })
    url = f"{SOV2EX_API}?{params}"
    r = fetch_json(url)
    if check_error(r):
        return []

    hits = r.get("hits", [])
    items = []
    for hit in hits:
        source = hit.get("_source", {})
        items.append({
            "id": source.get("id", ""),
            "title": source.get("title", ""),
            "content": source.get("content", ""),
            "node": source.get("node", ""),
            "member": source.get("member", ""),
            "replies": source.get("replies", 0),
            "created": source.get("created", ""),
        })
    return items


def _search_duckduckgo(keyword):
    """Fallback search via DuckDuckGo."""
    query = urllib.parse.quote(f"{keyword} site:v2ex.com/t/")
    url = f"https://html.duckduckgo.com/html/?q={query}"
    req = urllib.request.Request(url, headers={
        "User-Agent": HEADERS["User-Agent"],
        "Accept": "text/html",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            page = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"搜索失败: {e}")
        return []

    results = re.findall(
        r'<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>(.*?)</a>',
        page,
    )
    snippets = re.findall(
        r'<a class="result__snippet"[^>]*>(.*?)</a>',
        page,
        re.DOTALL,
    )

    items = []
    for i, (raw_link, raw_title) in enumerate(results):
        title = strip_html(raw_title)
        snippet = strip_html(snippets[i]) if i < len(snippets) else ""

        m = re.search(r'uddg=([^&]+)', raw_link)
        link = urllib.parse.unquote(m.group(1)) if m else raw_link

        if "v2ex.com" not in link:
            continue

        tid_m = re.search(r'/t/(\d+)', link)
        items.append({
            "id": tid_m.group(1) if tid_m else "",
            "title": title,
            "content": snippet,
            "link": link,
        })
        if len(items) >= 15:
            break

    return items


def cmd_search(keyword):
    # Try SOV2EX first
    items = _search_sov2ex(keyword)
    if items:
        print(f"搜索「{keyword}」结果:\n")
        for i, item in enumerate(items, 1):
            tid = item["id"]
            title = item["title"]
            content = truncate(strip_html(item.get("content", "")), 150)
            node = item.get("node", "")
            member = item.get("member", "")
            replies = item.get("replies", 0)
            created = format_time(item.get("created", ""))

            node_str = f" [{node}]" if node else ""
            meta_parts = []
            if member:
                meta_parts.append(member)
            if replies:
                meta_parts.append(f"{replies}回复")
            if created:
                meta_parts.append(created)
            meta_str = "  ".join(meta_parts)

            print(f"{i}. {title}{node_str}")
            if content:
                print(f"   {content}")
            if meta_str:
                print(f"   {meta_str}")
            print(f"   https://www.v2ex.com/t/{tid}")
            if tid:
                print(f"   ID: {tid}")
            print()
        return

    # Fallback to DuckDuckGo
    items = _search_duckduckgo(keyword)
    if not items:
        print("未找到相关结果，请尝试其他关键词")
        return

    print(f"搜索「{keyword}」结果 (via DuckDuckGo):\n")
    for i, item in enumerate(items, 1):
        print(f"{i}. {item['title']}")
        if item.get("content"):
            print(f"   {truncate(item['content'], 150)}")
        link = item.get("link", f"https://www.v2ex.com/t/{item['id']}")
        print(f"   {link}")
        if item.get("id"):
            print(f"   ID: {item['id']}")
        print()


# ── Topic Detail ──────────────────────────────────────────────────────────

def cmd_topic(topic_id):
    url = f"{V2EX_API_V1}/topics/show.json?id={topic_id}"
    r = fetch_json(url)

    if check_error(r):
        return

    if isinstance(r, list) and r:
        topic = r[0]
    elif isinstance(r, dict) and "title" in r:
        topic = r
    else:
        print("主题不存在或获取失败")
        return

    title = topic.get("title", "")
    content = strip_html(topic.get("content_rendered", "") or topic.get("content", ""))
    member = topic.get("member", {})
    username = member.get("username", "") if isinstance(member, dict) else ""
    node = topic.get("node", {})
    node_name = node.get("title", "") if isinstance(node, dict) else ""
    node_slug = node.get("name", "") if isinstance(node, dict) else ""
    replies = topic.get("replies", 0)
    created = format_time(topic.get("created", ""))
    last_modified = format_time(topic.get("last_modified", ""))

    print(f"{title}")
    meta_parts = []
    if username:
        meta_parts.append(f"作者: {username}")
    if node_name:
        meta_parts.append(f"节点: {node_name}")
    if replies:
        meta_parts.append(f"{replies}回复")
    if created:
        meta_parts.append(f"发布: {created}")
    if meta_parts:
        print("  ".join(meta_parts))

    if content:
        print(f"\n{content}")

    print(f"\nhttps://www.v2ex.com/t/{topic_id}")


# ── Topic Replies ─────────────────────────────────────────────────────────

def cmd_replies(topic_id):
    url = f"{V2EX_API_V1}/replies/show.json?topic_id={topic_id}"
    r = fetch_json(url)

    if check_error(r):
        return

    if not isinstance(r, list):
        print("获取回复失败")
        return

    if not r:
        print("暂无回复")
        return

    print(f"主题 #{topic_id} 的回复 (共 {len(r)} 条):\n")
    for i, reply in enumerate(r, 1):
        member = reply.get("member", {})
        username = member.get("username", "") if isinstance(member, dict) else ""
        content = strip_html(reply.get("content_rendered", "") or reply.get("content", ""))
        created = format_time(reply.get("created", ""))
        thanks = reply.get("thanks", 0)

        thanks_str = f"  ({thanks}感谢)" if thanks else ""
        print(f"{i}. [{username}]{thanks_str}  {created}")
        print(f"   {content}")
        print()


# ── Hot Topics ────────────────────────────────────────────────────────────

def cmd_hot():
    url = f"{V2EX_API_V1}/topics/hot.json"
    r = fetch_json(url)

    if check_error(r):
        return

    if not isinstance(r, list):
        print("获取热门主题失败")
        return

    print("V2EX 热门主题:\n")
    for i, topic in enumerate(r, 1):
        title = topic.get("title", "")
        tid = topic.get("id", "")
        member = topic.get("member", {})
        username = member.get("username", "") if isinstance(member, dict) else ""
        node = topic.get("node", {})
        node_name = node.get("title", "") if isinstance(node, dict) else ""
        replies = topic.get("replies", 0)

        node_str = f" [{node_name}]" if node_name else ""
        meta_parts = []
        if username:
            meta_parts.append(username)
        if replies:
            meta_parts.append(f"{replies}回复")
        meta_str = "  ".join(meta_parts)

        print(f"{i}. {title}{node_str}")
        if meta_str:
            print(f"   {meta_str}")
        print(f"   https://www.v2ex.com/t/{tid}")
        print(f"   ID: {tid}")
        print()


# ── Latest Topics ─────────────────────────────────────────────────────────

def cmd_latest():
    url = f"{V2EX_API_V1}/topics/latest.json"
    r = fetch_json(url)

    if check_error(r):
        return

    if not isinstance(r, list):
        print("获取最新主题失败")
        return

    print("V2EX 最新主题:\n")
    for i, topic in enumerate(r, 1):
        title = topic.get("title", "")
        tid = topic.get("id", "")
        member = topic.get("member", {})
        username = member.get("username", "") if isinstance(member, dict) else ""
        node = topic.get("node", {})
        node_name = node.get("title", "") if isinstance(node, dict) else ""
        replies = topic.get("replies", 0)
        created = format_time(topic.get("created", ""))

        node_str = f" [{node_name}]" if node_name else ""
        meta_parts = []
        if username:
            meta_parts.append(username)
        if replies:
            meta_parts.append(f"{replies}回复")
        if created:
            meta_parts.append(created)
        meta_str = "  ".join(meta_parts)

        print(f"{i}. {title}{node_str}")
        if meta_str:
            print(f"   {meta_str}")
        print(f"   https://www.v2ex.com/t/{tid}")
        print(f"   ID: {tid}")
        print()


# ── Node Info ─────────────────────────────────────────────────────────────

def cmd_node(node_name):
    url = f"{V2EX_API_V1}/nodes/show.json?name={urllib.parse.quote(node_name)}"
    r = fetch_json(url)

    if check_error(r):
        return

    if not isinstance(r, dict) or "name" not in r:
        print("节点不存在或获取失败")
        return

    name = r.get("name", "")
    title = r.get("title", "")
    title_alt = r.get("title_alternative", "")
    topics = r.get("topics", 0)
    stars = r.get("stars", 0)
    header = strip_html(r.get("header", ""))
    footer = strip_html(r.get("footer", ""))

    print(f"{title}")
    if title_alt and title_alt != title:
        print(f"别名: {title_alt}")
    print(f"标识: {name}")
    print(f"主题数: {topics}  关注: {stars}")
    if header:
        print(f"\n{header}")
    if footer:
        print(f"\n{footer}")
    print(f"\nhttps://www.v2ex.com/go/{name}")


# ── Node Topics ───────────────────────────────────────────────────────────

def cmd_node_topics(node_name):
    url = f"{V2EX_API_V1}/topics/show.json?node_name={urllib.parse.quote(node_name)}"
    r = fetch_json(url)

    if check_error(r):
        return

    if not isinstance(r, list):
        print("获取节点主题失败")
        return

    if not r:
        print(f"节点 {node_name} 暂无主题")
        return

    print(f"节点「{node_name}」最新主题:\n")
    for i, topic in enumerate(r, 1):
        title = topic.get("title", "")
        tid = topic.get("id", "")
        member = topic.get("member", {})
        username = member.get("username", "") if isinstance(member, dict) else ""
        replies = topic.get("replies", 0)
        created = format_time(topic.get("created", ""))

        meta_parts = []
        if username:
            meta_parts.append(username)
        if replies:
            meta_parts.append(f"{replies}回复")
        if created:
            meta_parts.append(created)
        meta_str = "  ".join(meta_parts)

        print(f"{i}. {title}")
        if meta_str:
            print(f"   {meta_str}")
        print(f"   https://www.v2ex.com/t/{tid}")
        print(f"   ID: {tid}")
        print()


# ── User Profile ──────────────────────────────────────────────────────────

def cmd_user(username):
    url = f"{V2EX_API_V1}/members/show.json?username={urllib.parse.quote(username)}"
    r = fetch_json(url)

    if check_error(r):
        return

    if not isinstance(r, dict) or "username" not in r:
        print("用户不存在或获取失败")
        return

    uname = r.get("username", "")
    bio = r.get("bio", "")
    website = r.get("website", "")
    github = r.get("github", "")
    twitter = r.get("twitter", "")
    location = r.get("location", "")
    tagline = r.get("tagline", "")
    created = format_time(r.get("created", ""))

    print(f"{uname}")
    if tagline:
        print(f"  {tagline}")
    if bio:
        print(f"  简介: {bio}")
    if location:
        print(f"  位置: {location}")
    if website:
        print(f"  网站: {website}")
    if github:
        print(f"  GitHub: {github}")
    if twitter:
        print(f"  Twitter: {twitter}")
    if created:
        print(f"  注册: {created}")
    print(f"  https://www.v2ex.com/member/{uname}")


# ── User Topics ───────────────────────────────────────────────────────────

def cmd_user_topics(username):
    url = f"{V2EX_API_V1}/topics/show.json?username={urllib.parse.quote(username)}"
    r = fetch_json(url)

    if check_error(r):
        return

    if not isinstance(r, list):
        print("获取用户主题失败")
        return

    if not r:
        print(f"用户 {username} 暂无主题")
        return

    print(f"用户「{username}」的主题:\n")
    for i, topic in enumerate(r, 1):
        title = topic.get("title", "")
        tid = topic.get("id", "")
        node = topic.get("node", {})
        node_name = node.get("title", "") if isinstance(node, dict) else ""
        replies = topic.get("replies", 0)
        created = format_time(topic.get("created", ""))

        node_str = f" [{node_name}]" if node_name else ""
        meta_parts = []
        if replies:
            meta_parts.append(f"{replies}回复")
        if created:
            meta_parts.append(created)
        meta_str = "  ".join(meta_parts)

        print(f"{i}. {title}{node_str}")
        if meta_str:
            print(f"   {meta_str}")
        print(f"   https://www.v2ex.com/t/{tid}")
        print(f"   ID: {tid}")
        print()


# ── Import Token ──────────────────────────────────────────────────────────

def cmd_import_token():
    """Guide user to import V2EX API token."""
    print("=== 导入 V2EX Token ===\n")
    print("步骤:")
    print("  1. 登录 https://www.v2ex.com/")
    print("  2. 进入 设置 → Tokens (https://www.v2ex.com/settings/tokens)")
    print("  3. 创建新的 Personal Access Token")
    print(f"  4. 将 Token 保存到: {TOKEN_FILE}")
    print()
    print("保存方法:")
    print(f'  echo "你的token" > {TOKEN_FILE}')
    print()
    if os.path.exists(TOKEN_FILE):
        token = get_token()
        if token:
            masked = token[:8] + "..." + token[-4:] if len(token) > 12 else "***"
            print(f"当前状态: token.txt 已存在 ({masked})")
        else:
            print("当前状态: token.txt 存在但为空")
    else:
        print("当前状态: token.txt 不存在")


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "search": (cmd_search, 1),
        "topic": (cmd_topic, 1),
        "replies": (cmd_replies, 1),
        "hot": (cmd_hot, 0),
        "latest": (cmd_latest, 0),
        "node": (cmd_node, 1),
        "node-topics": (cmd_node_topics, 1),
        "user": (cmd_user, 1),
        "user-topics": (cmd_user_topics, 1),
        "import-token": (cmd_import_token, 0),
    }

    if cmd not in commands:
        print(f"未知命令: {cmd}")
        print(__doc__)
        sys.exit(1)

    func, nargs = commands[cmd]
    if len(args) < nargs:
        print(f"命令 '{cmd}' 需要 {nargs} 个参数")
        sys.exit(1)

    func(*args[:nargs])


if __name__ == "__main__":
    main()
