from unittest.mock import patch
from collectors.hacker_news import HackerNewsCollector
from collectors.base import Article


def test_collect_returns_articles():
    collector = HackerNewsCollector()
    articles = collector.collect()
    assert len(articles) > 0
    assert len(articles) <= 3
    for a in articles:
        assert isinstance(a, Article)
        assert a.title
        assert a.source == "Hacker News"
        assert a.category == "news"


def test_collect_filters_ai_related():
    collector = HackerNewsCollector()
    articles = collector.collect()
    ai_keywords = ["ai", "llm", "gpt", "model", "ml", "deep", "transformer",
                   "language", "neural", "openai", "anthropic", "gemini", "claude"]
    for a in articles:
        title_lower = a.title.lower()
        assert any(kw in title_lower for kw in ai_keywords), f"'{a.title}' is not AI-related"


def test_collect_handles_api_error():
    collector = HackerNewsCollector()
    with patch.object(collector, "_get", side_effect=Exception("API error")):
        articles = collector.collect()
        assert isinstance(articles, list)
        assert len(articles) == 0
