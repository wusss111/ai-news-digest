import json
import logging
import requests
from config import REQUEST_TIMEOUT

logger = logging.getLogger(__name__)


class FeishuSender:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, card: dict) -> bool:
        if not self.webhook_url:
            logger.warning("未配置 FEISHU_WEBHOOK_URL，跳过发送")
            return False

        payload = json.dumps(card, ensure_ascii=False).encode("utf-8")
        for attempt in range(2):
            try:
                resp = requests.post(
                    self.webhook_url,
                    data=payload,
                    headers={"Content-Type": "application/json; charset=utf-8"},
                    timeout=REQUEST_TIMEOUT,
                )
                if resp.status_code == 200:
                    result = resp.json()
                    if result.get("code") == 0:
                        logger.info("飞书发送成功")
                        return True
                    else:
                        logger.warning("飞书发送失败: %s", result.get("msg", "unknown"))
                else:
                    logger.warning("飞书 HTTP %d: %s", resp.status_code, resp.text[:200])
            except Exception:
                logger.exception("飞书请求异常 (attempt %d)", attempt + 1)
        return False
