from datetime import datetime, timedelta, timezone
from typing import List
import requests
from config import GITHUB_TOKEN, MAX_PER_SOURCE
from collectors.base import Article, BaseCollector


class GitHubTrendingCollector(BaseCollector):
    name = "GitHub"
    category = "project"

    def collect(self) -> List[Article]:
        articles = []
        try:
            headers = {
                "Accept": "application/vnd.github+json",
            }
            if GITHUB_TOKEN:
                headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

            # 搜索最近一周创建的 AI/ML 相关仓库，按 stars 排序
            since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
            query = f"topic:machine-learning+created:>{since}"
            url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page={MAX_PER_SOURCE['github']}"

            resp = self._get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            for repo in data.get("items", [])[:MAX_PER_SOURCE["github"]]:
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
        except Exception as e:
            print(f"[GitHub] 采集失败: {e}")
        return articles
