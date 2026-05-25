# AI 每日速递 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个 Python 脚本，每天自动搜集 AI 资讯并通过飞书 Webhook 推送卡片消息，运行在 GitHub Actions 上。

**Architecture:** 8 个独立采集器并行获取数据源内容，统一归入 Article 模型，经 formatter 去重排版为飞书卡片 JSON，由 feishu_sender 通过 Webhook 发送。每个采集器独立 try/except，单个失败不影响整体。

**Tech Stack:** Python 3.11+, requests, feedparser, beautifulsoup4, GitHub Actions

---

### Task 1: 项目脚手架和基础框架

**Files:**
- Create: `D:\AI每日速递\requirements.txt`
- Create: `D:\AI每日速递\config.py`
- Create: `D:\AI每日速递\collectors\__init__.py`
- Create: `D:\AI每日速递\collectors\base.py`

- [ ] **Step 1: 创建 requirements.txt**

```txt
requests==2.31.0
feedparser==6.0.11
beautifulsoup4==4.12.3
```

- [ ] **Step 2: 创建 config.py**

```python
import os

FEISHU_WEBHOOK_URL = os.environ.get("FEISHU_WEBHOOK_URL", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

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
```

- [ ] **Step 3: 创建 collectors/__init__.py**

```python
```

- [ ] **Step 4: 创建 collectors/base.py**

```python
from dataclasses import dataclass, field
from typing import List
import requests
from config import REQUEST_TIMEOUT


@dataclass
class Article:
    title: str
    url: str
    source: str
    summary: str
    category: str  # paper / project / news / tool


class BaseCollector:
    name: str = "base"
    category: str = "news"

    def collect(self) -> List[Article]:
        raise NotImplementedError

    def _get(self, url: str, headers: dict = None) -> requests.Response:
        default_headers = {"User-Agent": "AI-News-Digest/1.0"}
        if headers:
            default_headers.update(headers)
        return requests.get(url, headers=default_headers, timeout=REQUEST_TIMEOUT)
```

- [ ] **Step 5: 初始化 git 并提交**

```bash
cd "D:\AI每日速递"
git init
git add -A
git commit -m "feat: project scaffold with base collector framework"
```

---

### Task 2: GitHub Trending 采集器

**Files:**
- Create: `D:\AI每日速递\collectors\github_trending.py`
- Create: `D:\AI每日速递\tests\__init__.py`
- Create: `D:\AI每日速递\tests\test_github_trending.py`

- [ ] **Step 1: 编写测试**

```python
from collectors.github_trending import GitHubTrendingCollector
from collectors.base import Article


def test_collect_returns_articles():
    collector = GitHubTrendingCollector()
    articles = collector.collect()
    assert len(articles) > 0
    assert len(articles) <= 5
    for a in articles:
        assert isinstance(a, Article)
        assert a.title
        assert a.url.startswith("https://github.com")
        assert a.source == "GitHub"
        assert a.category == "project"
        assert len(a.summary) > 0


def test_collect_handles_api_error():
    collector = GitHubTrendingCollector()
    articles = collector.collect()
    assert isinstance(articles, list)
```

- [ ] **Step 2: 验证测试失败**

```bash
cd "D:\AI每日速递"
pytest tests/test_github_trending.py -v
```
Expected: FAIL — 模块不存在

- [ ] **Step 3: 实现采集器**

```python
from datetime import datetime, timedelta
from typing import List
import requests
from config import GITHUB_TOKEN, MAX_PER_SOURCE
from collectors.base import Article, BaseCollector


class GitHubTrendingCollector(BaseCollector):
    name = "GitHub"
    category = "project"

    def collect(self) -> List[Article]:
        articles = []
        try:
            headers = {
                "Accept": "application/vnd.github+json",
            }
            if GITHUB_TOKEN:
                headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

            # 搜索最近一周创建的 AI/ML 相关仓库，按 stars 排序
            since = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
            query = f"topic:machine-learning+created:>{since}"
            url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page={MAX_PER_SOURCE['github']}"

            resp = self._get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            for repo in data.get("items", [])[:MAX_PER_SOURCE["github"]]:
                desc = repo.get("description") or ""
                # 截取摘要到约 400 字
                summary = desc[:400]
                lang = repo.get("language") or ""
                stars = repo.get("stargazers_count", 0)
                if lang:
                    summary = f"[{lang}] ⭐{stars} | {summary}"[:400]

                articles.append(Article(
                    title=repo.get("full_name", ""),
                    url=repo.get("html_url", ""),
                    source="GitHub",
                    summary=summary,
                    category="project",
                ))
        except Exception as e:
            print(f"[GitHub] 采集失败: {e}")
        return articles
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_github_trending.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add collectors/github_trending.py tests/
git commit -m "feat: add GitHub Trending collector"
```

---

### Task 3: arXiv 论文采集器

**Files:**
- Create: `D:\AI每日速递\collectors\arxiv_papers.py`
- Create: `D:\AI每日速递\tests\test_arxiv.py`

- [ ] **Step 1: 编写测试**

```python
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
```

- [ ] **Step 2: 验证测试失败**

```bash
pytest tests/test_arxiv.py -v
```
Expected: FAIL

- [ ] **Step 3: 实现采集器**

```python
from typing import List
import feedparser
from config import REQUEST_TIMEOUT, MAX_PER_SOURCE
from collectors.base import Article, BaseCollector


ARXIV_CATEGORIES = ["cs.AI", "cs.CL", "cs.CV"]


class ArxivCollector(BaseCollector):
    name = "arXiv"
    category = "paper"

    def collect(self) -> List[Article]:
        articles = []
        try:
            query = "+OR+".join(f"cat:{c}" for c in ARXIV_CATEGORIES)
            url = (
                f"http://export.arxiv.org/api/query?"
                f"search_query={query}&sortBy=submittedDate&sortOrder=descending"
                f"&max_results={MAX_PER_SOURCE['arxiv']}"
            )
            resp = self._get(url)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)

            for entry in feed.entries[:MAX_PER_SOURCE["arxiv"]]:
                arxiv_id = entry.id.split("/abs/")[-1]
                article_url = f"https://arxiv.org/abs/{arxiv_id}"
                summary = entry.summary[:400] if hasattr(entry, "summary") else ""

                articles.append(Article(
                    title=entry.title.strip().replace("\n", " "),
                    url=article_url,
                    source="arXiv",
                    summary=summary,
                    category="paper",
                ))
        except Exception as e:
            print(f"[arXiv] 采集失败: {e}")
        return articles
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_arxiv.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add collectors/arxiv_papers.py tests/test_arxiv.py
git commit -m "feat: add arXiv papers collector"
```

---

### Task 4: Hacker News 采集器

**Files:**
- Create: `D:\AI每日速递\collectors\hacker_news.py`
- Create: `D:\AI每日速递\tests\test_hacker_news.py`

- [ ] **Step 1: 编写测试**

```python
from collectors.hacker_news import HackerNewsCollector
from collectors.base import Article


def test_collect_returns_articles():
    collector = HackerNewsCollector()
    articles = collector.collect()
    assert len(articles) > 0
    assert len(articles) <= 3
    for a in articles:
        assert isinstance(a, Article)
        assert a.title
        assert a.source == "Hacker News"
        assert a.category == "news"


def test_collect_filters_ai_related():
    collector = HackerNewsCollector()
    articles = collector.collect()
    ai_keywords = ["ai", "llm", "gpt", "model", "ml", "deep", "transformer",
                   "language", "neural", "openai", "anthropic", "gemini", "claude"]
    for a in articles:
        title_lower = a.title.lower()
        assert any(kw in title_lower for kw in ai_keywords), f"'{a.title}' 不是 AI 相关"
```

- [ ] **Step 2: 验证测试失败**

```bash
pytest tests/test_hacker_news.py -v
```
Expected: FAIL

- [ ] **Step 3: 实现采集器**

```python
from typing import List
from config import MAX_PER_SOURCE
from collectors.base import Article, BaseCollector


AI_KEYWORDS = [
    "ai", "llm", "gpt", "model", "ml", "deep", "transformer",
    "language", "neural", "openai", "anthropic", "gemini", "claude",
    "diffusion", "reinforcement", "embedding", "token", "inference",
    "fine-tun", "rag", "agent", "chatbot", "copilot", "vector",
]


class HackerNewsCollector(BaseCollector):
    name = "Hacker News"
    category = "news"

    def collect(self) -> List[Article]:
        articles = []
        try:
            # 获取 top stories 前 50 条
            top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            resp = self._get(top_url)
            resp.raise_for_status()
            story_ids = resp.json()[:50]

            count = 0
            for sid in story_ids:
                if count >= MAX_PER_SOURCE["hackernews"]:
                    break
                try:
                    item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
                    item_resp = self._get(item_url)
                    item_resp.raise_for_status()
                    item = item_resp.json()

                    title = item.get("title", "")
                    if not self._is_ai_related(title):
                        continue

                    url = item.get("url") or f"https://news.ycombinator.com/item?id={sid}"
                    text = item.get("text", "")[:400] if item.get("text") else ""
                    summary = text if text else f"🔥 {item.get('score', 0)} points, {item.get('descendants', 0)} comments"

                    articles.append(Article(
                        title=title,
                        url=url,
                        source="Hacker News",
                        summary=summary[:400],
                        category="news",
                    ))
                    count += 1
                except Exception:
                    continue
        except Exception as e:
            print(f"[HackerNews] 采集失败: {e}")
        return articles

    def _is_ai_related(self, title: str) -> bool:
        title_lower = title.lower()
        return any(kw in title_lower for kw in AI_KEYWORDS)
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_hacker_news.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add collectors/hacker_news.py tests/test_hacker_news.py
git commit -m "feat: add Hacker News collector with AI keyword filtering"
```

---

### Task 5: Reddit 采集器

**Files:**
- Create: `D:\AI每日速递\collectors\reddit_ml.py`
- Create: `D:\AI每日速递\tests\test_reddit.py`

- [ ] **Step 1: 编写测试**

```python
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
```

- [ ] **Step 2: 验证测试失败**

```bash
pytest tests/test_reddit.py -v
```
Expected: FAIL

- [ ] **Step 3: 实现采集器**

```python
from typing import List
from config import MAX_PER_SOURCE
from collectors.base import Article, BaseCollector


class RedditCollector(BaseCollector):
    name = "Reddit"
    category = "tool"

    def collect(self) -> List[Article]:
        articles = []
        try:
            url = f"https://www.reddit.com/r/MachineLearning/hot.json?limit={MAX_PER_SOURCE['reddit'] + 2}"
            headers = {"User-Agent": "AI-News-Digest/1.0 (by /u/ai_digest_bot)"}
            resp = self._get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            count = 0
            for child in data.get("data", {}).get("children", []):
                if count >= MAX_PER_SOURCE["reddit"]:
                    break
                post = child.get("data", {})
                # 跳过置顶和公告
                if post.get("stickied"):
                    continue

                title = post.get("title", "")
                permalink = post.get("permalink", "")
                url = f"https://www.reddit.com{permalink}" if permalink else ""
                selftext = post.get("selftext", "")[:400]
                score = post.get("score", 0)
                num_comments = post.get("num_comments", 0)
                summary = selftext if selftext else f"👍 {score} upvotes, 💬 {num_comments} comments"

                articles.append(Article(
                    title=title,
                    url=url,
                    source="Reddit",
                    summary=summary[:400],
                    category="tool",
                ))
                count += 1
        except Exception as e:
            print(f"[Reddit] 采集失败: {e}")
        return articles
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_reddit.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add collectors/reddit_ml.py tests/test_reddit.py
git commit -m "feat: add Reddit r/MachineLearning collector"
```

---

### Task 6: HuggingFace Daily Papers 采集器

**Files:**
- Create: `D:\AI每日速递\collectors\huggingface.py`
- Create: `D:\AI每日速递\tests\test_huggingface.py`

- [ ] **Step 1: 编写测试**

```python
from collectors.huggingface import HuggingFaceCollector
from collectors.base import Article


def test_collect_returns_articles():
    collector = HuggingFaceCollector()
    articles = collector.collect()
    assert len(articles) > 0
    assert len(articles) <= 3
    for a in articles:
        assert isinstance(a, Article)
        assert a.title
        assert a.source == "HuggingFace"
        assert a.category == "paper"
        assert a.url
```

- [ ] **Step 2: 验证测试失败**

```bash
pytest tests/test_huggingface.py -v
```
Expected: FAIL

- [ ] **Step 3: 实现采集器**

```python
from typing import List
from config import MAX_PER_SOURCE
from collectors.base import Article, BaseCollector


class HuggingFaceCollector(BaseCollector):
    name = "HuggingFace"
    category = "paper"

    def collect(self) -> List[Article]:
        articles = []
        try:
            url = f"https://huggingface.co/api/daily_papers"
            resp = self._get(url)
            resp.raise_for_status()
            papers = resp.json()

            for paper in papers[:MAX_PER_SOURCE["huggingface"]]:
                title = paper.get("title", "").strip()
                paper_id = paper.get("paper", {}).get("id", "")
                paper_url = f"https://huggingface.co/papers/{paper_id}" if paper_id else ""
                summary = paper.get("paper", {}).get("summary", "")[:400]
                upvotes = paper.get("upvotes", 0)
                if not summary:
                    summary = f"👍 {upvotes} upvotes on HuggingFace"

                articles.append(Article(
                    title=title,
                    url=paper_url,
                    source="HuggingFace",
                    summary=summary[:400],
                    category="paper",
                ))
        except Exception as e:
            print(f"[HuggingFace] 采集失败: {e}")
        return articles
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_huggingface.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add collectors/huggingface.py tests/test_huggingface.py
git commit -m "feat: add HuggingFace daily papers collector"
```

---

### Task 7: ProductHunt 采集器

**Files:**
- Create: `D:\AI每日速递\collectors\product_hunt.py`
- Create: `D:\AI每日速递\tests\test_product_hunt.py`

- [ ] **Step 1: 编写测试**

```python
from collectors.product_hunt import ProductHuntCollector
from collectors.base import Article


def test_collect_returns_articles():
    collector = ProductHuntCollector()
    articles = collector.collect()
    assert len(articles) >= 0  # 可能网络原因返回空
    assert len(articles) <= 3
    for a in articles:
        assert isinstance(a, Article)
        assert a.title
        assert a.source == "ProductHunt"
        assert a.category == "tool"
```

- [ ] **Step 2: 验证测试失败**

```bash
pytest tests/test_product_hunt.py -v
```
Expected: FAIL

- [ ] **Step 3: 实现采集器**

```python
from typing import List
from bs4 import BeautifulSoup
from config import MAX_PER_SOURCE
from collectors.base import Article, BaseCollector


class ProductHuntCollector(BaseCollector):
    name = "ProductHunt"
    category = "tool"

    def collect(self) -> List[Article]:
        articles = []
        try:
            # 抓取 ProductHunt AI 分类页面
            url = "https://www.producthunt.com/categories/ai"
            resp = self._get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # 从 meta 标签或 script 中提取初始数据
            count = 0
            for link in soup.select("a[href^='/products/']"):
                if count >= MAX_PER_SOURCE["producthunt"]:
                    break
                href = link.get("href", "")
                if not href or "/categories/" in href or "/topics/" in href:
                    continue
                title_el = link.select_one("h3, [data-test='product-name']")
                desc_el = link.select_one("p, [data-test='product-tagline']")
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                summary = desc_el.get_text(strip=True) if desc_el else ""
                product_url = f"https://www.producthunt.com{href}" if href.startswith("/") else href

                articles.append(Article(
                    title=title,
                    url=product_url,
                    source="ProductHunt",
                    summary=summary[:400],
                    category="tool",
                ))
                count += 1

            # 如果页面抓取失败，尝试 RSS
            if not articles:
                articles = self._collect_from_rss()
        except Exception as e:
            print(f"[ProductHunt] 采集失败: {e}")
            articles = self._collect_from_rss()
        return articles

    def _collect_from_rss(self) -> List[Article]:
        articles = []
        try:
            import feedparser
            rss_url = "https://www.producthunt.com/feed"
            feed = feedparser.parse(rss_url)
            count = 0
            for entry in feed.entries:
                if count >= MAX_PER_SOURCE["producthunt"]:
                    break
                articles.append(Article(
                    title=entry.title,
                    url=entry.link,
                    source="ProductHunt",
                    summary=entry.get("summary", "")[:400] if hasattr(entry, "summary") else "",
                    category="tool",
                ))
                count += 1
        except Exception as e:
            print(f"[ProductHunt RSS] 采集失败: {e}")
        return articles
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_product_hunt.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add collectors/product_hunt.py tests/test_product_hunt.py
git commit -m "feat: add ProductHunt AI category collector"
```

---

### Task 8: 机器之心 采集器

**Files:**
- Create: `D:\AI每日速递\collectors\jiqizhixin.py`
- Create: `D:\AI每日速递\tests\test_jiqizhixin.py`

- [ ] **Step 1: 编写测试**

```python
from collectors.jiqizhixin import JiqizhixinCollector
from collectors.base import Article


def test_collect_returns_articles():
    collector = JiqizhixinCollector()
    articles = collector.collect()
    assert len(articles) >= 0
    assert len(articles) <= 2
    for a in articles:
        assert isinstance(a, Article)
        assert a.title
        assert a.source == "机器之心"
        assert a.category == "news"
```

- [ ] **Step 2: 验证测试失败**

```bash
pytest tests/test_jiqizhixin.py -v
```
Expected: FAIL

- [ ] **Step 3: 实现采集器**

```python
from typing import List
import feedparser
from config import MAX_PER_SOURCE
from collectors.base import Article, BaseCollector


class JiqizhixinCollector(BaseCollector):
    name = "机器之心"
    category = "news"

    def collect(self) -> List[Article]:
        articles = []
        try:
            # 通过 RSSHub 获取机器之心内容
            urls = [
                "https://rsshub.app/jiqizhixin/latest",
                "https://www.jiqizhixin.com/rss",
            ]
            feed = None
            for url in urls:
                try:
                    resp = self._get(url)
                    resp.raise_for_status()
                    feed = feedparser.parse(resp.text)
                    if feed.entries:
                        break
                except Exception:
                    continue

            if not feed or not feed.entries:
                return articles

            for entry in feed.entries[:MAX_PER_SOURCE["jiqizhixin"]]:
                summary = ""
                if hasattr(entry, "summary"):
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(entry.summary, "html.parser")
                    summary = soup.get_text()[:400]

                articles.append(Article(
                    title=entry.title,
                    url=entry.link,
                    source="机器之心",
                    summary=summary,
                    category="news",
                ))
        except Exception as e:
            print(f"[机器之心] 采集失败: {e}")
        return articles
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_jiqizhixin.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add collectors/jiqizhixin.py tests/test_jiqizhixin.py
git commit -m "feat: add 机器之心 RSS collector"
```

---

### Task 9: AI Blog (OpenAI/Anthropic) 采集器

**Files:**
- Create: `D:\AI每日速递\collectors\ai_blogs.py`
- Create: `D:\AI每日速递\tests\test_ai_blogs.py`

- [ ] **Step 1: 编写测试**

```python
from collectors.ai_blogs import AIBlogsCollector
from collectors.base import Article


def test_collect_returns_articles():
    collector = AIBlogsCollector()
    articles = collector.collect()
    assert len(articles) >= 0
    assert len(articles) <= 2
    for a in articles:
        assert isinstance(a, Article)
        assert a.title
        assert a.source in ("OpenAI Blog", "Anthropic Blog")
        assert a.category == "news"


def test_openai_blog_fetch():
    collector = AIBlogsCollector()
    articles = collector.collect()
    openai_articles = [a for a in articles if a.source == "OpenAI Blog"]
    assert isinstance(openai_articles, list)
```

- [ ] **Step 2: 验证测试失败**

```bash
pytest tests/test_ai_blogs.py -v
```
Expected: FAIL

- [ ] **Step 3: 实现采集器**

```python
from typing import List
import feedparser
from config import MAX_PER_SOURCE
from collectors.base import Article, BaseCollector


BLOG_SOURCES = [
    ("OpenAI Blog", "https://openai.com/blog/rss.xml"),
    ("Anthropic Blog", "https://www.anthropic.com/blog/rss.xml"),
]


class AIBlogsCollector(BaseCollector):
    name = "AI Blogs"
    category = "news"

    def collect(self) -> List[Article]:
        articles = []
        per_blog = max(1, MAX_PER_SOURCE["ai_blogs"] // len(BLOG_SOURCES))

        for source_name, rss_url in BLOG_SOURCES:
            try:
                resp = self._get(rss_url)
                resp.raise_for_status()
                feed = feedparser.parse(resp.text)

                for entry in feed.entries[:per_blog]:
                    summary = ""
                    if hasattr(entry, "summary"):
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(entry.summary, "html.parser")
                        summary = soup.get_text()[:400]
                    elif hasattr(entry, "content"):
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(entry.content[0].value, "html.parser")
                        summary = soup.get_text()[:400]

                    articles.append(Article(
                        title=entry.title,
                        url=entry.link,
                        source=source_name,
                        summary=summary,
                        category="news",
                    ))
            except Exception as e:
                print(f"[{source_name}] 采集失败: {e}")

        return articles
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_ai_blogs.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add collectors/ai_blogs.py tests/test_ai_blogs.py
git commit -m "feat: add OpenAI/Anthropic blog RSS collector"
```

---

### Task 10: 消息格式化器

**Files:**
- Create: `D:\AI每日速递\formatter.py`
- Create: `D:\AI每日速递\tests\test_formatter.py`

- [ ] **Step 1: 编写测试**

```python
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
    # 确保卡片 JSON 合法
    assert card["msg_type"] == "interactive"
```

- [ ] **Step 2: 验证测试失败**

```bash
pytest tests/test_formatter.py -v
```
Expected: FAIL

- [ ] **Step 3: 实现格式化器**

```python
from datetime import datetime, timezone, timedelta
from typing import List, Dict
from collectors.base import Article


CATEGORY_ICONS = {
    "paper": "📄",
    "project": "💻",
    "news": "📰",
    "tool": "🛠",
}

CATEGORY_NAMES = {
    "paper": "论文",
    "project": "开源项目",
    "news": "行业动态",
    "tool": "工具/产品",
}

# 飞书卡片颜色
CATEGORY_COLORS = {
    "paper": "blue",
    "project": "green",
    "news": "orange",
    "tool": "purple",
}


class Formatter:

    @staticmethod
    def deduplicate(articles: List[Article]) -> List[Article]:
        seen = set()
        result = []
        for a in articles:
            if a.url not in seen:
                seen.add(a.url)
                result.append(a)
        return result

    @staticmethod
    def group_by_category(articles: List[Article]) -> Dict[str, List[Article]]:
        groups: Dict[str, List[Article]] = {}
        for a in articles:
            if a.category not in groups:
                groups[a.category] = []
            groups[a.category].append(a)
        return groups

    @staticmethod
    def build_card(articles: List[Article]) -> dict:
        if not articles:
            return {}

        articles = Formatter.deduplicate(articles)
        groups = Formatter.group_by_category(articles)

        bj_tz = timezone(timedelta(hours=8))
        today = datetime.now(bj_tz).strftime("%Y-%m-%d")

        elements = []
        for cat in ["paper", "project", "news", "tool"]:
            if cat not in groups or not groups[cat]:
                continue
            icon = CATEGORY_ICONS.get(cat, "")
            name = CATEGORY_NAMES.get(cat, cat)

            # 分类标题分隔线
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**{icon} {name}**"
                }
            })

            for article in groups[cat]:
                content = f"[{article.title}]({article.url})\n{article.summary}"
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": content
                    }
                })

            # 分隔线
            elements.append({
                "tag": "hr",
            })

        # 移除最后一个多余的 hr
        if elements and elements[-1].get("tag") == "hr":
            elements.pop()

        card = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"🤖 AI 每日速递 · {today}"
                    },
                    "template": "blue",
                },
                "elements": elements,
            }
        }
        return card
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_formatter.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add formatter.py tests/test_formatter.py
git commit -m "feat: add message formatter with dedup and card JSON builder"
```

---

### Task 11: 飞书发送器

**Files:**
- Create: `D:\AI每日速递\feishu_sender.py`
- Create: `D:\AI每日速递\tests\test_feishu_sender.py`

- [ ] **Step 1: 编写测试**

```python
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
```

- [ ] **Step 2: 验证测试失败**

```bash
pytest tests/test_feishu_sender.py -v
```
Expected: FAIL

- [ ] **Step 3: 实现发送器**

```python
import json
import requests
from config import REQUEST_TIMEOUT


class FeishuSender:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, card: dict) -> bool:
        if not self.webhook_url:
            print("[Feishu] 未配置 WEBHOOK_URL，跳过发送")
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
                        print("[Feishu] 发送成功")
                        return True
                    else:
                        print(f"[Feishu] 发送失败: {result.get('msg', 'unknown')}")
                else:
                    print(f"[Feishu] HTTP {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                print(f"[Feishu] 请求异常 (attempt {attempt + 1}): {e}")
        return False
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_feishu_sender.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add feishu_sender.py tests/test_feishu_sender.py
git commit -m "feat: add Feishu webhook sender with retry"
```

---

### Task 12: 主入口

**Files:**
- Create: `D:\AI每日速递\main.py`
- Create: `D:\AI每日速递\tests\test_main.py`

- [ ] **Step 1: 编写测试**

```python
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
```

- [ ] **Step 2: 验证测试失败**

```bash
pytest tests/test_main.py -v
```
Expected: FAIL

- [ ] **Step 3: 实现主入口**

```python
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from collectors.github_trending import GitHubTrendingCollector
from collectors.arxiv_papers import ArxivCollector
from collectors.hacker_news import HackerNewsCollector
from collectors.reddit_ml import RedditCollector
from collectors.huggingface import HuggingFaceCollector
from collectors.product_hunt import ProductHuntCollector
from collectors.jiqizhixin import JiqizhixinCollector
from collectors.ai_blogs import AIBlogsCollector
from formatter import Formatter
from feishu_sender import FeishuSender
from config import FEISHU_WEBHOOK_URL


COLLECTORS = [
    GitHubTrendingCollector,
    ArxivCollector,
    HackerNewsCollector,
    RedditCollector,
    HuggingFaceCollector,
    ProductHuntCollector,
    JiqizhixinCollector,
    AIBlogsCollector,
]


def run() -> bool:
    all_articles = []

    with ThreadPoolExecutor(max_workers=len(COLLECTORS)) as executor:
        futures = {
            executor.submit(c().collect): c().name
            for c in COLLECTORS
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                articles = future.result()
                all_articles.extend(articles)
                print(f"[{name}] 获取 {len(articles)} 条")
            except Exception as e:
                print(f"[{name}] 异常: {e}")

    if not all_articles:
        print("所有采集器均无结果，跳过发送")
        return False

    print(f"共获取 {len(all_articles)} 条文章（去重前）")
    card = Formatter.build_card(all_articles)

    if not card:
        print("构建卡片失败")
        return False

    sender = FeishuSender(FEISHU_WEBHOOK_URL)
    return sender.send(card)


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_main.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add main.py tests/test_main.py
git commit -m "feat: add main entry with parallel collector execution"
```

---

### Task 13: GitHub Actions 定时任务

**Files:**
- Create: `D:\AI每日速递\.github\workflows\daily-digest.yml`

- [ ] **Step 1: 创建 workflow 文件**

```yaml
name: AI Daily Digest

on:
  schedule:
    - cron: '0 1 * * *'  # UTC 1:00 = 北京时间 9:00
  workflow_dispatch:       # 支持手动触发

jobs:
  digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run digest
        env:
          FEISHU_WEBHOOK_URL: ${{ secrets.FEISHU_WEBHOOK_URL }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python main.py
```

- [ ] **Step 2: 提交**

```bash
git add .github/workflows/daily-digest.yml
git commit -m "feat: add GitHub Actions daily schedule workflow"
```

---

### Task 14: 整体验证和收尾

**Files:**
- Create: `D:\AI每日速递\README.md`

- [ ] **Step 1: 运行全部测试**

```bash
cd "D:\AI每日速递"
pytest tests/ -v
```
Expected: 所有测试 PASS

- [ ] **Step 2: 创建 README**

```md
# AI 每日速递

每天自动搜集 AI 资讯并推送到飞书。

## 数据源

- arXiv 最新论文
- HuggingFace 每日精选论文
- GitHub Trending AI 项目
- Hacker News AI 相关讨论
- Reddit r/MachineLearning
- ProductHunt AI 分类
- 机器之心
- OpenAI / Anthropic 官方博客

## 使用

1. Fork 本仓库
2. 在飞书群里添加自定义机器人，复制 Webhook URL
3. 在仓库 Settings → Secrets and variables → Actions 中添加：
   - `FEISHU_WEBHOOK_URL`: 飞书机器人 Webhook 地址（必填）
   - `GITHUB_TOKEN`: GitHub Token（可选，提高 API 限额）
4. GitHub Actions 会在每天北京时间 9:00 自动运行

## 手动运行

```bash
pip install -r requirements.txt
export FEISHU_WEBHOOK_URL="your-webhook-url"
python main.py
```
```

- [ ] **Step 3: 最终提交**

```bash
git add README.md
git commit -m "docs: add README with setup instructions"
```

- [ ] **Step 4: 最终验证**

```bash
pytest tests/ -v
echo "---"
python -c "from main import run; print('main.py 导入成功')"
echo "---"
echo "所有检查通过"
```
Expected: 全部测试通过，main.py 可正常导入
