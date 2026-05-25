from collectors.arxiv_papers import ArxivCollector
from collectors.base import Article


def test_collect_returns_articles():
    collector = ArxivCollector()
    articles = collector.collect()
    assert len(articles) > 0
    assert len(articles) <= 3
    for a in articles:
        assert isinstance(a, Article)
        assert a.title
        assert a.url.startswith("https://arxiv.org")
        assert a.source == "arXiv"
        assert a.category == "paper"
        assert len(a.summary) > 0
