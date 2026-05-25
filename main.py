import sys
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from collectors.github_trending import GitHubTrendingCollector
from collectors.arxiv_papers import ArxivCollector
from collectors.hacker_news import HackerNewsCollector
from collectors.reddit_ml import RedditCollector
from collectors.huggingface import HuggingFaceCollector
from collectors.product_hunt import ProductHuntCollector
from collectors.jiqizhixin import JiqizhixinCollector
from collectors.ai_blogs import AIBlogsCollector
from formatter import Formatter
from feishu_sender import FeishuSender
from config import FEISHU_WEBHOOK_URL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

COLLECTORS = [
    GitHubTrendingCollector,
    ArxivCollector,
    HackerNewsCollector,
    RedditCollector,
    HuggingFaceCollector,
    ProductHuntCollector,
    JiqizhixinCollector,
    AIBlogsCollector,
]


def run() -> bool:
    all_articles = []

    with ThreadPoolExecutor(max_workers=len(COLLECTORS)) as executor:
        futures = {
            executor.submit(c().collect): c().name
            for c in COLLECTORS
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                articles = future.result()
                all_articles.extend(articles)
                logger.info("[%s] 获取 %d 条", name, len(articles))
            except Exception:
                logger.exception("[%s] 异常", name)

    if not all_articles:
        logger.warning("所有采集器均无结果，跳过发送")
        return False

    logger.info("共获取 %d 条文章（去重前）", len(all_articles))
    card = Formatter.build_card(all_articles)

    if not card:
        logger.error("构建卡片失败")
        return False

    sender = FeishuSender(FEISHU_WEBHOOK_URL)
    return sender.send(card)


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
