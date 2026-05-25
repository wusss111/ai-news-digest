# AI 每日速递 — 设计文档

## 概述

每天自动搜集最新 AI 资讯（论文、开源项目、行业动态、工具产品），整理为一条飞书卡片消息，定时推送到手机飞书。

## 数据源

| 源 | 分类 | 方式 | 条数 |
|---|---|---|---|
| arXiv API | 📄 论文 | API，搜索 cs.AI / cs.CL / cs.CV | 3 |
| HuggingFace Daily Papers | 📄 论文 | 社区精选 API | 3 |
| GitHub Trending | 💻 项目 | GitHub API + trending 页面解析 | 5 |
| Hacker News API | 📰 动态 | HN API，筛选 AI 相关 | 3 |
| 机器之心 RSS | 📰 动态 | RSS | 2 |
| OpenAI / Anthropic Blog RSS | 📰 动态 | RSS | 2 |
| ProductHunt AI 分类 | 🛠 工具 | RSS / 页面解析 | 3 |
| Reddit r/MachineLearning | 🛠 工具 | Reddit JSON API | 3 |

## 技术栈

- Python 3.11+
- requests / feedparser / beautifulsoup4
- GitHub Actions（定时调度 + 运行环境）

## 架构

```
GitHub Actions (UTC 1:00 daily)
    │
    ▼
main.py（入口：并行执行采集器，汇总数据）
    │
    ├──> collectors/github_trending.py
    ├──> collectors/arxiv_papers.py
    ├──> collectors/hacker_news.py
    ├──> collectors/reddit_ml.py
    ├──> collectors/huggingface.py
    ├──> collectors/product_hunt.py
    ├──> collectors/jiqizhixin.py
    └──> collectors/ai_blogs.py
    │
    ▼
formatter.py（去重 + 渲染飞书卡片 JSON）
    │
    ▼
feishu_sender.py（POST 飞书 Webhook）
    │
    ▼
用户手机飞书收到卡片消息
```

## 统一数据模型

```python
@dataclass
class Article:
    title: str          # 标题
    url: str            # 链接
    source: str         # 来源标签
    summary: str        # 摘要，约 400 字
    category: str       # paper / project / news / tool
```

每个采集器返回 `list[Article]`，最多返回配置的条数上限。

## 卡片消息结构

一条飞书卡片消息，包含四个分类区块：

- 📄 论文（arXiv + HuggingFace，共 6 条）
- 💻 开源项目（GitHub，共 5 条）
- 📰 行业动态（HN + 机器之心 + AI Blog，共 7 条）
- 🛠 工具/产品（ProductHunt + Reddit，共 6 条）

每条含标题链接和约 400 字摘要，使用飞书 card 的 markdown block 渲染。

## 项目结构

```
ai-news-digest/
├── main.py
├── collectors/
│   ├── __init__.py
│   ├── base.py
│   ├── github_trending.py
│   ├── arxiv_papers.py
│   ├── hacker_news.py
│   ├── reddit_ml.py
│   ├── huggingface.py
│   ├── product_hunt.py
│   ├── jiqizhixin.py
│   └── ai_blogs.py
├── formatter.py
├── feishu_sender.py
├── config.py
├── requirements.txt
└── .github/workflows/
    └── daily-digest.yml
```

## 配置

通过环境变量配置，敏感信息存入 GitHub Secrets：

| 变量 | 用途 | 必须 |
|---|---|---|
| `FEISHU_WEBHOOK_URL` | 飞书自定义机器人 Webhook | ✅ |
| `GITHUB_TOKEN` | GitHub API 提高限流额度 | 建议 |
| `REDDIT_CLIENT_ID` | Reddit API（可选，公开 JSON 也可用） | 否 |
| `REDDIT_SECRET` | Reddit API Secret | 否 |

## 错误处理

- 每个采集器独立 try/except，超时 30 秒，失败跳过不影响其他源
- 所有采集器都失败 → 不发消息，任务标记 failed
- 飞书发送失败 → 重试 1 次，仍失败则标记 failed

## 飞书推送

- 方式：自定义机器人 Webhook
- 搭建：飞书群 → 设置 → 群机器人 → 添加自定义机器人 → 复制 Webhook URL
- 目标群可只有用户一人
- 消息格式：飞书 Interactive Card（`interactive` 消息类型）

## 调度

GitHub Actions cron：`0 1 * * *`（UTC 1:00 = 北京时间 9:00）

## 费用

零费用。所有 API 和平台在用量内均免费。
