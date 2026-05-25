from typing import List
import logging
from config import MAX_PER_SOURCE
from collectors.base import Article, BaseCollector

logger = logging.getLogger(__name__)

AI_KEYWORDS = [
    "ai", "llm", "gpt", "model", "ml", "deep", "transformer",
    "language", "neural", "openai", "anthropic", "gemini", "claude",
    "diffusion", "reinforcement", "embedding", "token", "inference",
    "fine-tun", "rag", "agent", "chatbot", "copilot", "vector",
]


class HackerNewsCollector(BaseCollector):
    name = "Hacker News"
    category = "news"

    def collect(self) -> List[Article]:
        articles = []
        try:
            top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            resp = self._get(top_url)
            resp.raise_for_status()
            story_ids = resp.json()[:50]

            count = 0
            for sid in story_ids:
                if count >= MAX_PER_SOURCE["hackernews"]:
                    break
                try:
                    item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
                    item_resp = self._get(item_url)
                    item_resp.raise_for_status()
                    item = item_resp.json()

                    title = item.get("title", "")
                    if not self._is_ai_related(title):
                        continue

                    url = item.get("url") or f"https://news.ycombinator.com/item?id={sid}"
                    score = item.get("score", 0)
                    descendants = item.get("descendants", 0)
                    summary = f"🔥 {score} points, {descendants} comments"

                    articles.append(Article(
                        title=title,
                        url=url,
                        source="Hacker News",
                        summary=summary[:400],
                        category="news",
                    ))
                    count += 1
                except Exception:
                    continue
        except Exception:
            logger.exception("[HackerNews] 采集失败")
        return articles

    def _is_ai_related(self, title: str) -> bool:
        title_lower = title.lower()
        return any(kw in title_lower for kw in AI_KEYWORDS)
