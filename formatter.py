from datetime import datetime, timezone, timedelta
from typing import List, Dict
from collectors.base import Article


CATEGORY_ICONS = {
    "paper": "📄",
    "project": "💻",
    "news": "📰",
    "tool": "🛠",
}

CATEGORY_NAMES = {
    "paper": "论文",
    "project": "开源项目",
    "news": "行业动态",
    "tool": "工具/产品",
}


class Formatter:

    @staticmethod
    def deduplicate(articles: List[Article]) -> List[Article]:
        seen = set()
        result = []
        for a in articles:
            if a.url not in seen:
                seen.add(a.url)
                result.append(a)
        return result

    @staticmethod
    def group_by_category(articles: List[Article]) -> Dict[str, List[Article]]:
        groups: Dict[str, List[Article]] = {}
        for a in articles:
            if a.category not in groups:
                groups[a.category] = []
            groups[a.category].append(a)
        return groups

    @staticmethod
    def build_card(articles: List[Article]) -> dict:
        if not articles:
            return {}

        articles = Formatter.deduplicate(articles)
        groups = Formatter.group_by_category(articles)

        bj_tz = timezone(timedelta(hours=8))
        today = datetime.now(bj_tz).strftime("%Y-%m-%d")

        elements = []
        for cat in ["paper", "project", "news", "tool"]:
            if cat not in groups or not groups[cat]:
                continue
            icon = CATEGORY_ICONS.get(cat, "")
            name = CATEGORY_NAMES.get(cat, cat)

            # 分类标题
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**{icon} {name}**"
                }
            })

            for article in groups[cat]:
                content = f"[{article.title}]({article.url})\n{article.summary}"
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": content
                    }
                })

            # 分隔线
            elements.append({
                "tag": "hr",
            })

        # 移除最后一个多余的 hr
        if elements and elements[-1].get("tag") == "hr":
            elements.pop()

        card = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"🤖 AI 每日速递 · {today}"
                    },
                    "template": "blue",
                },
                "elements": elements,
            }
        }
        return card
