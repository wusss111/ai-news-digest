import json
from unittest.mock import patch, Mock
from summarizer import summarize, _build_prompt, _parse_response
from collectors.base import Article


def make_articles(n=3):
    return [
        Article(f"Title {i}", f"https://example.com/{i}", f"Source{i}",
                f"English summary {i}", "news")
        for i in range(n)
    ]


def make_deepseek_response(summaries_list):
    content = json.dumps({"summaries": summaries_list}, ensure_ascii=False)
    return {
        "choices": [
            {"message": {"content": content}, "finish_reason": "stop"}
        ]
    }


def test_build_prompt_includes_article_data():
    articles_data = [
        {"index": 0, "title": "GPT-5 Released", "source": "OpenAI", "summary": "Big model"}
    ]
    prompt = _build_prompt(articles_data)
    assert "GPT-5 Released" in prompt
    assert "AI 资讯" in prompt
    assert "index" in prompt


def test_parse_response_with_summaries_key():
    summaries = [{"index": 0, "summary_zh": "这是一个测试"}]
    resp = make_deepseek_response(summaries)
    result = _parse_response(resp)
    assert result[0]["summary_zh"] == "这是一个测试"


def test_parse_response_direct_array():
    content = json.dumps([{"index": 0, "summary_zh": "直接数组"}], ensure_ascii=False)
    resp = {"choices": [{"message": {"content": content}}]}
    result = _parse_response(resp)
    assert result[0]["summary_zh"] == "直接数组"


def test_parse_response_no_choices_returns_none():
    result = _parse_response({"choices": []})
    assert result is None


def test_parse_response_invalid_json_returns_none():
    resp = {"choices": [{"message": {"content": "not valid json!!!"}}]}
    result = _parse_response(resp)
    assert result is None


def test_summarize_empty_list():
    result = summarize([])
    assert result == []


def test_summarize_no_api_key_returns_unchanged():
    articles = make_articles(2)
    with patch("summarizer.DEEPSEEK_API_KEY", ""):
        result = summarize(articles)
    assert result is articles
    assert all(a.summary.startswith("English") for a in result)


@patch("summarizer.requests.post")
@patch("summarizer.DEEPSEEK_API_KEY", "sk-test-key")
def test_summarize_success(mock_post):
    articles = make_articles(2)
    resp = Mock()
    resp.json.return_value = make_deepseek_response([
        {"index": 0, "summary_zh": "GPT-5 是最新的大语言模型"},
        {"index": 1, "summary_zh": "一个自动化测试工具"},
    ])
    mock_post.return_value = resp

    result = summarize(articles)
    assert result[0].summary == "GPT-5 是最新的大语言模型"
    assert result[1].summary == "一个自动化测试工具"
    mock_post.assert_called_once()


@patch("summarizer.requests.post")
@patch("summarizer.DEEPSEEK_API_KEY", "sk-test-key")
def test_summarize_network_error_returns_unchanged(mock_post):
    articles = make_articles(2)
    mock_post.side_effect = ConnectionError("timeout")
    result = summarize(articles)
    assert result is articles
    assert all(a.summary.startswith("English") for a in result)


@patch("summarizer.requests.post")
@patch("summarizer.DEEPSEEK_API_KEY", "sk-test-key")
def test_summarize_partial_response_applies_only_valid(mock_post):
    articles = make_articles(3)
    resp = Mock()
    resp.json.return_value = make_deepseek_response([
        {"index": 0, "summary_zh": "第一篇文章"},
        {"index": 2, "summary_zh": "第三篇文章"},
    ])
    mock_post.return_value = resp

    result = summarize(articles)
    assert result[0].summary == "第一篇文章"
    assert result[1].summary == "English summary 1"
    assert result[2].summary == "第三篇文章"
