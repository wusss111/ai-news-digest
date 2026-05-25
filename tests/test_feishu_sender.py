import json
from unittest.mock import patch, Mock
from feishu_sender import FeishuSender


def test_send_success():
    card = {"msg_type": "interactive", "card": {"header": {"title": {"tag": "plain_text", "content": "test"}}}}
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"code": 0, "msg": "success"}

    with patch("feishu_sender.requests.post", return_value=mock_resp) as mock_post:
        sender = FeishuSender(webhook_url="https://fake-webhook.com")
        result = sender.send(card)
        assert result is True
        mock_post.assert_called_once()


def test_send_failure_retry():
    card = {"msg_type": "interactive", "card": {}}
    mock_fail = Mock()
    mock_fail.status_code = 500
    mock_success = Mock()
    mock_success.status_code = 200
    mock_success.json.return_value = {"code": 0}

    with patch("feishu_sender.requests.post", side_effect=[mock_fail, mock_success]) as mock_post:
        sender = FeishuSender(webhook_url="https://fake-webhook.com")
        result = sender.send(card)
        assert result is True
        assert mock_post.call_count == 2


def test_send_no_webhook():
    sender = FeishuSender(webhook_url="")
    result = sender.send({})
    assert result is False
