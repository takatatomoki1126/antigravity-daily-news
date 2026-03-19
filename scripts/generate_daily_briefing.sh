#!/bin/bash
# Antigravity Daily Briefing — 自動生成スクリプト
# launchd から毎日 07:00 JST に実行される

set -euo pipefail

WORK_DIR="/Users/tomoki/daily-briefing"
LOG="$WORK_DIR/briefing_cron.log"

echo "=== $(date '+%Y-%m-%d %H:%M:%S') 起動 ===" >> "$LOG"

# claude CLI を探す (バージョンが変わっても対応できるよう動的に検索)
CLAUDE=$(find "$HOME/Library/Application Support/Claude" -name "claude" -type f 2>/dev/null | sort -V | tail -1)

if [ -z "$CLAUDE" ]; then
  echo "ERROR: claude CLI が見つかりません" >> "$LOG"
  exit 1
fi

echo "claude: $CLAUDE" >> "$LOG"
cd "$WORK_DIR"

"$CLAUDE" --dangerously-skip-permissions -p "$(cat <<'PROMPT'
今日のAntigravity Daily Executive Briefingを生成してください。

手順:
1. WebFetchで以下のRSSからニュース5件ずつ取得
   - AI: https://news.google.com/rss/search?q=AI+Google+Gemini+ChatGPT&hl=ja&gl=JP&ceid=JP:ja
   - 日本: https://news.google.com/rss/search?q=日本+政治+経済&hl=ja&gl=JP&ceid=JP:ja
   - 台湾: https://news.google.com/rss/search?q=台湾+中国+関係&hl=ja&gl=JP&ceid=JP:ja
   - Tech: https://news.google.com/rss/search?q=tech+AI+startup&hl=ja&gl=JP&ceid=JP:ja
2. WebFetchで為替取得: https://www.xe.com/currencyconverter/convert/?Amount=1&From=TWD&To=JPY
3. 各ニュースに日本語要約＋【詳細概要】(Antigravity視点のインサイト)を書く
4. Steve Jobs・Sam Altman・Jeff Bezos・Elon Muskのディベート形式でマルチエージェント分析を書く
5. /Users/tomoki/daily-briefing/daily_briefings/Briefing_YYYY-MM-DD.md に書き込む（今日の日付）
6. /Users/tomoki/daily-briefing/daily_briefings/dates.json を更新する（daily_briefings/内の全.mdファイルの日付を新しい順でJSONとして出力）
7. git add, commit "docs: generate YYYY-MM-DD briefing with full AI summaries via Claude", push origin main を実行する

フォーマットは /Users/tomoki/daily-briefing/daily_briefings/Briefing_2026-03-17.md を参照すること。
PROMPT
)" >> "$LOG" 2>&1

echo "=== $(date '+%Y-%m-%d %H:%M:%S') 完了 ===" >> "$LOG"
