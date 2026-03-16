import os
import datetime
import json
import time
from scripts.operations.daily_trend_crawler import fetch_exchange_rate
from ai_workspace.core.multi_agent_analyzer import analyze_trends, enhance_news_with_summary
from scripts.generators.daily_briefing_generator import generate_daily_briefing
from duckduckgo_search import DDGS

def fetch_past_news(date_str, query, limit=3):
    """DuckDuckGoを使用してニュースを検索"""
    print(f"  - Searching for '{query}'...")
    extracted = []
    try:
        with DDGS() as ddgs:
            # 最新のニュース検索 (ddgs.news) を使用
            # 過去日はキーワードに含める
            q = f"{query} {date_str}"
            results = list(ddgs.news(q, max_results=limit))
            
            if not results:
                print(f"    No results for '{q}', trying '{query}' generic...")
                results = list(ddgs.news(query, max_results=limit))
            
            for r in results:
                extracted.append({
                    "title": r.get('title', 'No Title'),
                    "link": r.get('url', 'No Link'), # ddgs.news では 'url' キー
                    "summary": r.get('body', '')
                })
            print(f"    Found {len(extracted)} items.")
    except Exception as e:
        print(f"    Error searching news for {query}: {e}")
    return extracted

def backfill(date_str):
    print(f"--- Backfilling for {date_str} ---")
    
    # 日付オブジェクトを作成
    target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    
    # 既存のジェネレーターが datetime.datetime.now() を使っている箇所を考慮し
    # 慎重にモック。ここではdatetimeクラス自体をクラス継承でラップするのではなく
    # 単純にその日付で各処理を実行できるように工夫する。
    # scripts/generators/daily_briefing_generator.py の generate_daily_briefing を確認。
    
    try:
        # 1. 為替
        print("Step 1: Fetching Indicators...")
        rate_info = fetch_exchange_rate()
        
        # 2. ニュース収集
        print("Step 2: Fetching Past News via DuckDuckGo...")
        all_data = {
            "exchange_rate": rate_info,
            "japan_news": fetch_past_news(date_str, "日本 ニュース", 5),
            "taiwan_news": fetch_past_news(date_str, "台湾 中国 情勢", 5),
            "tech_news": fetch_past_news(date_str, "global tech trends", 3),
            "ai_news": fetch_past_news(date_str, "Google AI Antigravity", 3)
        }
        
        # 3. 要約の強化
        print("Step 3: Enhancing news with AI summaries...")
        for category in ['japan_news', 'taiwan_news', 'tech_news', 'ai_news']:
            if all_data.get(category):
                all_data[category] = enhance_news_with_summary(all_data[category])
        
        # 4. 分析
        print("Step 4: Multi-Agent Analysis...")
        analysis_result = analyze_trends(all_data)
        
        # 5. レポート生成
        # daily_briefing_generator.py の内部で datetime.datetime.now() を使ってファイル名や見出しを作っているため
        # 呼び出し時だけ monkeypatch する。
        import scripts.generators.daily_briefing_generator as generator
        original_dt = generator.datetime.datetime
        
        class MockDT:
            @staticmethod
            def now(): return target_date
            @staticmethod
            def strptime(s, f): return original_dt.strptime(s, f)
            # その他必要なメソッドがあれば適宜
        
        generator.datetime.datetime = MockDT # generatorモジュール内でのみ有効
        
        try:
            print("Step 5: Generating Report...")
            report_path = generator.generate_daily_briefing(analysis_result, all_data)
            print(f"Generated: {report_path}")
        finally:
            generator.datetime.datetime = original_dt

    except Exception as e:
        print(f"Error backfilling {date_str}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    dates = ["2026-03-13", "2026-03-14", "2026-03-15"]
    for d in dates:
        backfill(d)
        time.sleep(2) # レート制限対策
