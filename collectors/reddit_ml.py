from typing import List
import logging
from config import MAX_PER_SOURCE
from collectors.base import Article, BaseCollector

logger = logging.getLogger(__name__)


class RedditCollector(BaseCollector):
    name = "Reddit"
    category = "tool"

    def collect(self) -> List[Article]:
        articles = []
        try:
            url = f"https://www.reddit.com/r/MachineLearning/hot.json?limit={MAX_PER_SOURCE['reddit'] + 2}"
            headers = {"User-Agent": "AI-News-Digest/1.0 (by /u/ai_digest_bot)"}
            resp = self._get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            count = 0
            for child in data.get("data", {}).get("children", []):
                if count >= MAX_PER_SOURCE["reddit"]:
                    break
                post = child.get("data", {})
                if post.get("stickied"):
                    continue

                title = post.get("title", "")
                permalink = post.get("permalink", "")
                url = f"https://www.reddit.com{permalink}" if permalink else ""
                selftext = post.get("selftext", "")[:400]
                score = post.get("score", 0)
                num_comments = post.get("num_comments", 0)
                summary = selftext if selftext else f"👍 {score} upvotes, 💬 {num_comments} comments"

                articles.append(Article(
                    title=title,
                    url=url,
                    source="Reddit",
                    summary=summary[:400],
                    category="tool",
                ))
                count += 1
        except Exception:
            logger.exception("[Reddit] 采集失败")
        return articles
