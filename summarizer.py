import json
import logging
from typing import List
import requests
from config import DEEPSEEK_API_KEY, REQUEST_TIMEOUT
from collectors.base import Article

logger = logging.getLogger(__name__)

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"
MAX_TOKENS = 2000

_SYSTEM_PROMPT = (
    "你是一位专业的 AI 资讯编辑。你的任务是用简洁的中文（1-2 句话）总结每一条 AI 资讯，"
    "清楚说明这个工具、论文或项目的内容和用途。"
    "返回 JSON 对象，包含 summaries 数组，每个元素有 index 和 summary_zh 字段。"
    "summary_zh 约 200-400 字，不要复制英文原文。"
)


def summarize(articles: List[Article]) -> List[Article]:
    if not articles:
        return articles

    if not DEEPSEEK_API_KEY:
        logger.warning("DEEPSEEK_API_KEY 未设置，跳过中文摘要")
        return articles

    articles_data = [
        {"index": i, "title": a.title, "source": a.source, "summary": a.summary}
        for i, a in enumerate(articles)
    ]

    prompt = _build_prompt(articles_data)

    try:
        resp = requests.post(
            DEEPSEEK_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": MAX_TOKENS,
                "temperature": 0.3,
            },
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
    except Exception:
        logger.exception("DeepSeek API 请求失败，使用原始摘要")
        return articles

    summaries = _parse_response(resp.json())
    if summaries is None:
        return articles

    updated = 0
    for item in summaries:
        idx = item.get("index")
        zh = item.get("summary_zh", "")
        if isinstance(idx, int) and 0 <= idx < len(articles) and zh:
            articles[idx].summary = zh
            updated += 1

    logger.info("已生成 %d/%d 条中文摘要", updated, len(articles))
    return articles


def _build_prompt(articles_data: list) -> str:
    lines = [
        "以下是今天收集到的 AI 资讯列表，请为每一条生成中文摘要（约 200-400 字），",
        "说明这个工具、论文或项目是做什么的、有什么亮点。",
        "",
        json.dumps(articles_data, ensure_ascii=False),
    ]
    return "\n".join(lines)


def _parse_response(response_json: dict) -> list | None:
    try:
        choices = response_json.get("choices", [])
        if not choices:
            logger.warning("DeepSeek 响应中没有 choices")
            return None
        content = choices[0].get("message", {}).get("content", "")
        parsed = json.loads(content)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict) and "summaries" in parsed:
            return parsed["summaries"]
        logger.warning("无法解析 DeepSeek 响应格式: %s", str(parsed)[:200])
        return None
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.warning("解析 DeepSeek 响应失败: %s", e)
        return None
