import os

FEISHU_WEBHOOK_URL = os.environ.get("FEISHU_WEBHOOK_URL", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

# 每条来源最多抓取条数
MAX_PER_SOURCE = {
    "arxiv": 3,
    "huggingface": 3,
    "github": 5,
    "hackernews": 3,
    "jiqizhixin": 2,
    "ai_blogs": 2,
    "producthunt": 3,
    "reddit": 3,
}

# 请求超时（秒）
REQUEST_TIMEOUT = 30
