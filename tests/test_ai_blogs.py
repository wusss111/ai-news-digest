from collectors.ai_blogs import AIBlogsCollector
from collectors.base import Article


def test_collect_returns_articles():
    collector = AIBlogsCollector()
    articles = collector.collect()
    assert len(articles) >= 0
    assert len(articles) <= 2
    for a in articles:
        assert isinstance(a, Article)
        assert a.title
        assert a.source in ("OpenAI Blog", "Anthropic Blog")
        assert a.category == "news"


def test_openai_blog_fetch():
    collector = AIBlogsCollector()
    articles = collector.collect()
    openai_articles = [a for a in articles if a.source == "OpenAI Blog"]
    assert isinstance(openai_articles, list)
