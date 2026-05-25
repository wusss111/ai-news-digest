from typing import List
import logging
import feedparser
from bs4 import BeautifulSoup
from config import MAX_PER_SOURCE
from collectors.base import Article, BaseCollector

logger = logging.getLogger(__name__)

BLOG_SOURCES = [
    ("OpenAI Blog", "https://openai.com/blog/rss.xml"),
    ("Anthropic Blog", "https://www.anthropic.com/blog/rss.xml"),
]


class AIBlogsCollector(BaseCollector):
    name = "AI Blogs"
    category = "news"

    def collect(self) -> List[Article]:
        articles = []
        per_blog = max(1, MAX_PER_SOURCE["ai_blogs"] // len(BLOG_SOURCES))

        for source_name, rss_url in BLOG_SOURCES:
            try:
                resp = self._get(rss_url)
                resp.raise_for_status()
                feed = feedparser.parse(resp.text)

                for entry in feed.entries[:per_blog]:
                    summary = ""
                    if hasattr(entry, "summary"):
                        soup = BeautifulSoup(entry.summary, "html.parser")
                        summary = soup.get_text()[:400]
                    elif hasattr(entry, "content"):
                        soup = BeautifulSoup(entry.content[0].value, "html.parser")
                        summary = soup.get_text()[:400]

                    articles.append(Article(
                        title=entry.title,
                        url=entry.link,
                        source=source_name,
                        summary=summary,
                        category="news",
                    ))
            except Exception:
                logger.exception("[%s] 采集失败", source_name)

        return articles
