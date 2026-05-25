from typing import List
import logging
import feedparser
from config import MAX_PER_SOURCE
from collectors.base import Article, BaseCollector

logger = logging.getLogger(__name__)


class ProductHuntCollector(BaseCollector):
    name = "ProductHunt"
    category = "tool"

    def collect(self) -> List[Article]:
        articles = []
        try:
            rss_url = "https://www.producthunt.com/feed"
            resp = self._get(rss_url)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)

            count = 0
            for entry in feed.entries:
                if count >= MAX_PER_SOURCE["producthunt"]:
                    break
                summary = ""
                if hasattr(entry, "summary"):
                    summary = entry.summary[:400]

                articles.append(Article(
                    title=entry.title,
                    url=entry.link,
                    source="ProductHunt",
                    summary=summary,
                    category="tool",
                ))
                count += 1
        except Exception:
            logger.exception("[ProductHunt] 采集失败")
        return articles
