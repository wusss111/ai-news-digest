from unittest.mock import patch, Mock
from main import run


def test_run_with_articles():
    mock_article = Mock()
    mock_article.title = "Test"
    mock_article.url = "https://test.com"
    mock_article.source = "Test"
    mock_article.summary = "Summary"
    mock_article.category = "news"

    with patch("main.GitHubTrendingCollector") as mock_gh, \
         patch("main.ArxivCollector") as mock_arx, \
         patch("main.HackerNewsCollector") as mock_hn, \
         patch("main.RedditCollector") as mock_red, \
         patch("main.HuggingFaceCollector") as mock_hf, \
         patch("main.ProductHuntCollector") as mock_ph, \
         patch("main.JiqizhixinCollector") as mock_jz, \
         patch("main.AIBlogsCollector") as mock_bl, \
         patch("main.Formatter") as mock_fmt, \
         patch("main.FeishuSender") as mock_sender, \
         patch("main.FEISHU_WEBHOOK_URL", "https://test.com"):
        mock_gh.return_value.collect.return_value = [mock_article]
        mock_arx.return_value.collect.return_value = []
        mock_hn.return_value.collect.return_value = [mock_article]
        mock_red.return_value.collect.return_value = [mock_article]
        mock_hf.return_value.collect.return_value = []
        mock_ph.return_value.collect.return_value = []
        mock_jz.return_value.collect.return_value = []
        mock_bl.return_value.collect.return_value = []
        mock_fmt.build_card.return_value = {"msg_type": "interactive"}
        mock_sender.return_value.send.return_value = True

        result = run()
        assert result is True


def test_run_all_collectors_fail():
    with patch("main.GitHubTrendingCollector") as mock_gh, \
         patch("main.ArxivCollector") as mock_arx, \
         patch("main.HackerNewsCollector") as mock_hn, \
         patch("main.RedditCollector") as mock_red, \
         patch("main.HuggingFaceCollector") as mock_hf, \
         patch("main.ProductHuntCollector") as mock_ph, \
         patch("main.JiqizhixinCollector") as mock_jz, \
         patch("main.AIBlogsCollector") as mock_bl:
        mock_gh.return_value.collect.return_value = []
        mock_arx.return_value.collect.return_value = []
        mock_hn.return_value.collect.return_value = []
        mock_red.return_value.collect.return_value = []
        mock_hf.return_value.collect.return_value = []
        mock_ph.return_value.collect.return_value = []
        mock_jz.return_value.collect.return_value = []
        mock_bl.return_value.collect.return_value = []

        result = run()
        assert result is False
