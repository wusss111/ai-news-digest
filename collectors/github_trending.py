from datetime import datetime, timedelta, timezone
import logging
from typing import List
from config import GITHUB_TOKEN, MAX_PER_SOURCE
from collectors.base import Article, BaseCollector

logger = logging.getLogger(__name__)


class GitHubTrendingCollector(BaseCollector):
    name = "GitHub"
    category = "project"

    def collect(self) -> List[Article]:
        articles = []
        try:
            if not GITHUB_TOKEN:
                logger.warning("GITHUB_TOKEN 未设置，API 限流为 60次/小时")

            headers = {
                "Accept": "application/vnd.github+json",
            }
            if GITHUB_TOKEN:
                headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

            since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
            query = f"topic:machine-learning+created:>{since}"
            url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page={MAX_PER_SOURCE['github']}"

            resp = self._get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            for repo in data.get("items", []):
                desc = repo.get("description") or ""
                lang = repo.get("language") or ""
                stars = repo.get("stargazers_count", 0)
                prefix = f"[{lang}] " if lang else ""
                summary = f"{prefix}⭐{stars} | {desc}"[:400]

                articles.append(Article(
                    title=repo.get("full_name", ""),
                    url=repo.get("html_url", ""),
                    source="GitHub",
                    summary=summary,
                    category="project",
                ))
        except Exception:
            logger.exception("[GitHub] 采集失败")
        return articles
