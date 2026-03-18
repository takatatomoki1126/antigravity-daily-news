#!/bin/bash
# Antigravity Daily Briefing Generator
# 毎朝claudeが自動でニュースを調べてブリーフィングを生成・GitHubにプッシュする

CLAUDE="/Users/tomoki/Library/Application Support/Claude/claude-code/2.1.74/claude"
PROJECT_DIR="/Users/tomoki/daily-briefing"
LOG="$PROJECT_DIR/briefing_cron.log"
DATE=$(date +%Y-%m-%d)

echo "[$(date)] Starting briefing generation for $DATE" >> "$LOG"

cd "$PROJECT_DIR"

"$CLAUDE" --dangerously-skip-permissions -p "
今日 $DATE のAntigravity Daily Executive Briefingを生成してください。

以下の手順で実行してください：
1. WebFetchを使って下記4カテゴリのGoogle News RSSからニュースを取得する
   - AI/Google: https://news.google.com/rss/search?q=AI+Google+Gemini+ChatGPT&hl=ja&gl=JP&ceid=JP:ja
   - 日本: https://news.google.com/rss/search?q=日本+政治+経済&hl=ja&gl=JP&ceid=JP:ja
   - 台湾: https://news.google.com/rss/search?q=台湾+中国+関係&hl=ja&gl=JP&ceid=JP:ja
   - Tech: https://news.google.com/rss/search?q=tech+AI+startup&hl=ja&gl=JP&ceid=JP:ja
2. XE.comから為替レート(TWD/JPY)を取得: https://www.xe.com/currencyconverter/convert/?Amount=1&From=TWD&To=JPY
3. 各ニュース5件に日本語要約と【詳細概要】(Antigravity視点のインサイト)を書く
4. Steve Jobs・Sam Altman・Jeff Bezos・Elon Muskのディベート形式でマルチエージェント分析を書く
5. /Users/tomoki/daily-briefing/daily_briefings/Briefing_${DATE}.md に書き込む
6. git add, git commit, git push origin main を実行する

markdownフォーマットは既存のブリーフィング(Briefing_2026-03-16.md)に合わせること。
" >> "$LOG" 2>&1

echo "[$(date)] Done" >> "$LOG"
