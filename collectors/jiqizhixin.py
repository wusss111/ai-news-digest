from typing import List
import logging
import feedparser
from bs4 import BeautifulSoup
from config import MAX_PER_SOURCE
from collectors.base import Article, BaseCollector

logger = logging.getLogger(__name__)


class JiqizhixinCollector(BaseCollector):
    name = "机器之心"
    category = "news"

    def collect(self) -> List[Article]:
        articles = []
        try:
            urls = [
                "https://rsshub.app/jiqizhixin/latest",
                "https://www.jiqizhixin.com/rss",
            ]
            feed = None
            for url in urls:
                try:
                    resp = self._get(url)
                    resp.raise_for_status()
                    feed = feedparser.parse(resp.text)
                    if feed.entries:
                        break
                except Exception:
                    continue

            if not feed or not feed.entries:
                return articles

            for entry in feed.entries[:MAX_PER_SOURCE["jiqizhixin"]]:
                summary = ""
                if hasattr(entry, "summary"):
                    soup = BeautifulSoup(entry.summary, "html.parser")
                    summary = soup.get_text()[:400]

                articles.append(Article(
                    title=entry.title,
                    url=entry.link,
                    source="机器之心",
                    summary=summary,
                    category="news",
                ))
        except Exception:
            logger.exception("[机器之心] 采集失败")
        return articles
