from collectors.huggingface import HuggingFaceCollector
from collectors.base import Article


def test_collect_returns_articles():
    collector = HuggingFaceCollector()
    articles = collector.collect()
    assert len(articles) > 0
    assert len(articles) <= 3
    for a in articles:
        assert isinstance(a, Article)
        assert a.title
        assert a.source == "HuggingFace"
        assert a.category == "paper"
        assert a.url
