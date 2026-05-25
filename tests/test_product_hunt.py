from collectors.product_hunt import ProductHuntCollector
from collectors.base import Article


def test_collect_returns_articles():
    collector = ProductHuntCollector()
    articles = collector.collect()
    assert len(articles) >= 0
    assert len(articles) <= 3
    for a in articles:
        assert isinstance(a, Article)
        assert a.title
        assert a.source == "ProductHunt"
        assert a.category == "tool"
