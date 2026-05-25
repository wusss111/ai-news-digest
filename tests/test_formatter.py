from formatter import Formatter
from collectors.base import Article


def test_deduplicate_by_url():
    articles = [
        Article("Same", "https://a.com/1", "GitHub", "summary", "project"),
        Article("Same2", "https://a.com/1", "GitHub", "summary2", "project"),
        Article("Diff", "https://b.com/2", "arXiv", "summary3", "paper"),
    ]
    result = Formatter.deduplicate(articles)
    assert len(result) == 2
    urls = [a.url for a in result]
    assert urls == ["https://a.com/1", "https://b.com/2"]


def test_group_by_category():
    articles = [
        Article("P1", "url1", "arXiv", "s", "paper"),
        Article("P2", "url2", "HF", "s", "paper"),
        Article("N1", "url3", "HN", "s", "news"),
        Article("T1", "url4", "PH", "s", "tool"),
        Article("J1", "url5", "GitHub", "s", "project"),
    ]
    groups = Formatter.group_by_category(articles)
    assert "paper" in groups
    assert "news" in groups
    assert "tool" in groups
    assert "project" in groups
    assert len(groups["paper"]) == 2
    assert len(groups["project"]) == 1


def test_build_card_json_has_required_fields():
    articles = [
        Article("Test Paper", "https://x.com/1", "arXiv", "A summary here", "paper"),
        Article("Test Project", "https://x.com/2", "GitHub", "A project summary", "project"),
    ]
    card = Formatter.build_card(articles)
    assert card["msg_type"] == "interactive"
    assert "card" in card
    assert card["card"]["header"]["title"]["content"] != ""
    assert len(card["card"]["elements"]) > 0


def test_empty_articles_returns_empty_card():
    card = Formatter.build_card([])
    assert card == {}


def test_summary_truncation():
    articles = [
        Article("T", "url", "src", "短摘要", "news"),
    ]
    card = Formatter.build_card(articles)
    assert card["msg_type"] == "interactive"
