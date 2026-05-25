# AI 每日速递

每天自动搜集 AI 资讯并推送到飞书。

## 数据源

- **📄 论文** — arXiv (cs.AI/cs.CL/cs.CV) + HuggingFace Daily Papers
- **💻 开源项目** — GitHub Trending (machine-learning topic)
- **📰 行业动态** — Hacker News + 机器之心 + OpenAI/Anthropic Blog
- **🛠 工具/产品** — ProductHunt + Reddit r/MachineLearning

## 使用

1. Fork 本仓库
2. 在飞书群里添加自定义机器人，复制 Webhook URL
3. 在仓库 Settings → Secrets and variables → Actions → New repository secret 中添加：
   - `FEISHU_WEBHOOK_URL` — 飞书机器人 Webhook 地址（必填）
   - `GITHUB_TOKEN` — GitHub Token（可选，提高 API 限额）
4. GitHub Actions 会在每天北京时间 9:00 自动运行

## 手动运行

```bash
pip install -r requirements.txt
$env:FEISHU_WEBHOOK_URL="your-webhook-url"
python main.py
```

## 手动触发

在 GitHub 仓库的 Actions 标签页选择 "AI Daily Digest"，点击 "Run workflow"。
