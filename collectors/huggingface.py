from typing import List
import logging
from config import MAX_PER_SOURCE
from collectors.base import Article, BaseCollector

logger = logging.getLogger(__name__)


class HuggingFaceCollector(BaseCollector):
    name = "HuggingFace"
    category = "paper"

    def collect(self) -> List[Article]:
        articles = []
        try:
            url = "https://huggingface.co/api/daily_papers"
            resp = self._get(url)
            resp.raise_for_status()
            papers = resp.json()

            for paper in papers[:MAX_PER_SOURCE["huggingface"]]:
                title = paper.get("title", "").strip()
                paper_data = paper.get("paper", {})
                paper_id = paper_data.get("id", "")
                paper_url = f"https://huggingface.co/papers/{paper_id}" if paper_id else ""
                summary = paper_data.get("summary", "")[:400]
                upvotes = paper.get("upvotes", 0)
                if not summary:
                    summary = f"👍 {upvotes} upvotes on HuggingFace"

                articles.append(Article(
                    title=title,
                    url=paper_url,
                    source="HuggingFace",
                    summary=summary[:400],
                    category="paper",
                ))
        except Exception:
            logger.exception("[HuggingFace] 采集失败")
        return articles
