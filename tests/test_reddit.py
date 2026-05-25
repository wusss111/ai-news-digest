from unittest.mock import patch
from collectors.reddit_ml import RedditCollector
from collectors.base import Article


def test_collect_returns_articles():
    collector = RedditCollector()
    articles = collector.collect()
    assert len(articles) > 0
    assert len(articles) <= 3
    for a in articles:
        assert isinstance(a, Article)
        assert a.title
        assert a.source == "Reddit"
        assert a.category == "tool"
        assert a.url


def test_collect_skips_stickied():
    collector = RedditCollector()
    mock_data = {
        "data": {
            "children": [
                {"data": {"title": "Stickied Post", "permalink": "/r/ML/1", "stickied": True, "selftext": "", "score": 10, "num_comments": 3}},
                {"data": {"title": "Normal Post", "permalink": "/r/ML/2", "stickied": False, "selftext": "", "score": 5, "num_comments": 1}},
            ]
        }
    }
    with patch.object(collector, "_get") as mock_get:
        mock_get.return_value.json.return_value = mock_data
        mock_get.return_value.raise_for_status = lambda: None
        articles = collector.collect()
        assert len(articles) == 1
        assert articles[0].title == "Normal Post"


def test_collect_handles_api_error():
    collector = RedditCollector()
    with patch.object(collector, "_get", side_effect=Exception("API error")):
        articles = collector.collect()
        assert isinstance(articles, list)
        assert len(articles) == 0
