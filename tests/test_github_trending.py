from unittest.mock import patch
from collectors.github_trending import GitHubTrendingCollector
from collectors.base import Article


def test_collect_returns_articles():
    collector = GitHubTrendingCollector()
    articles = collector.collect()
    assert len(articles) > 0
    assert len(articles) <= 5
    for a in articles:
        assert isinstance(a, Article)
        assert a.title
        assert a.url.startswith("https://github.com")
        assert a.source == "GitHub"
        assert a.category == "project"
        assert len(a.summary) > 0


def test_collect_handles_api_error():
    collector = GitHubTrendingCollector()
    with patch.object(collector, "_get", side_effect=Exception("API error")):
        articles = collector.collect()
        assert isinstance(articles, list)
        assert len(articles) == 0
