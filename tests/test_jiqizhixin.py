from unittest.mock import patch
from collectors.jiqizhixin import JiqizhixinCollector
from collectors.base import Article


def test_collect_returns_articles():
    collector = JiqizhixinCollector()
    articles = collector.collect()
    assert len(articles) >= 0
    assert len(articles) <= 2
    for a in articles:
        assert isinstance(a, Article)
        assert a.title
        assert a.source == "机器之心"
        assert a.category == "news"


def test_collect_handles_api_error():
    collector = JiqizhixinCollector()
    with patch.object(collector, "_get", side_effect=Exception("API error")):
        articles = collector.collect()
        assert isinstance(articles, list)
        assert len(articles) == 0
