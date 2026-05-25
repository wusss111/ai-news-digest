from typing import List
import logging
import feedparser
from config import MAX_PER_SOURCE
from collectors.base import Article, BaseCollector

logger = logging.getLogger(__name__)

ARXIV_CATEGORIES = ["cs.AI", "cs.CL", "cs.CV"]


class ArxivCollector(BaseCollector):
    name = "arXiv"
    category = "paper"

    def collect(self) -> List[Article]:
        articles = []
        try:
            query = "+OR+".join(f"cat:{c}" for c in ARXIV_CATEGORIES)
            url = (
                f"http://export.arxiv.org/api/query?"
                f"search_query={query}&sortBy=submittedDate&sortOrder=descending"
                f"&max_results={MAX_PER_SOURCE['arxiv']}"
            )
            resp = self._get(url)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)

            for entry in feed.entries[:MAX_PER_SOURCE["arxiv"]]:
                arxiv_id = entry.id.split("/abs/")[-1]
                article_url = f"https://arxiv.org/abs/{arxiv_id}"
                summary = entry.summary[:400] if hasattr(entry, "summary") else ""

                articles.append(Article(
                    title=entry.title.strip().replace("\n", " "),
                    url=article_url,
                    source="arXiv",
                    summary=summary,
                    category="paper",
                ))
        except Exception:
            logger.exception("[arXiv] 采集失败")
        return articles
