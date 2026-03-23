---
description: 今日のDaily Briefingを生成してGitHubへデプロイする
---

# Daily Briefing 生成ワークフロー

「今日のぶん」「今日のブリーフィング」「/daily-briefing」と言われたら実行する。
システム時刻から今日の日付を確認すること。

## Step 1: ニュース＆為替取得

以下5つを**並列で** WebFetch する:

- AI/Google: `https://news.google.com/rss/search?q=AI+Google+Gemini+ChatGPT&hl=ja&gl=JP&ceid=JP:ja`
- 日本: `https://news.google.com/rss/search?q=日本+政治+経済&hl=ja&gl=JP&ceid=JP:ja`
- 台湾: `https://news.google.com/rss/search?q=台湾+中国+関係&hl=ja&gl=JP&ceid=JP:ja`
- Tech: `https://news.google.com/rss/search?q=tech+AI+startup&hl=ja&gl=JP&ceid=JP:ja`
- 為替: `https://www.xe.com/currencyconverter/convert/?Amount=1&From=TWD&To=JPY`

## Step 2: ブリーフィング執筆

取得したデータをもとに、以下の構成でMarkdownを書く（フォーマットは `daily_briefings/Briefing_2026-03-16.md` を参照）:

1. **ヘッダー** — 日付・ステータス
2. **為替** — 1 TWD = X JPY（XE.com出典・取得時刻）
3. **AI/Google** — ニュース5件、各件に要約＋【詳細概要】（Antigravity視点のインサイト）
4. **日本** — ニュース5件、同上
5. **台湾・中国関係** — ニュース5件、同上
6. **Global Tech** — ニュース5件、同上
7. **マルチエージェント分析** — Steve Jobs・Sam Altman・Jeff Bezos・Elon Muskのディベート形式

## Step 3: ファイル書き込み

`/Users/tomoki/daily-briefing/daily_briefings/Briefing_YYYY-MM-DD.md` に書き込む（今日の日付）。

## Step 4: dates.json 更新

`/Users/tomoki/daily-briefing/daily_briefings/dates.json` を更新する。
`daily_briefings/` 内の全 `.md` ファイルの日付を新しい順でJSON配列として出力する。

## Step 5: GitHubへプッシュ

```bash
cd /Users/tomoki/daily-briefing && git add daily_briefings/ && git commit -m "docs: generate YYYY-MM-DD briefing with full AI summaries via Claude" && git push origin main
```

## 完了報告

- 本日分の生成完了を伝える
- 注目ニュース3〜5件のサマリー（箇条書き）
- ダッシュボード: https://takatatomoki1126.github.io/antigravity-daily-news/
