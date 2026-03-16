#!/usr/bin/env python3
"""
The Autonomous Office - Main Execution Loop (Phase 11)
拡張クローラーを用いて日台ニュース・為替・Antigravity情報を取得し、
解析のちレポート生成する。
"""
import sys
import os

# パスを追加
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from scripts.operations.daily_trend_crawler import run_all_crawlers
from ai_workspace.core.multi_agent_analyzer import analyze_trends, enhance_news_with_summary
from scripts.generators.daily_briefing_generator import generate_daily_briefing

def run_autonomous_office():
    print("🚀 [Step 1] Yann LeCun (Crawler v2): 外部市場・為替・ニュース情報を一括収集しています...")
    all_data = run_all_crawlers()

    # 全ニュースの本文から日本語3行要約（Abstract）を作成
    print("🌐 [Step 1.5] Yoshua Bengio (NLP Editor): グローバルニュースのリンク先をスクレイピングし、日本語の3行要約（Abstract）を生成しています...")
    for category in ['japan_news', 'taiwan_news', 'tech_news', 'ai_news']:
        if all_data.get(category):
            all_data[category] = enhance_news_with_summary(all_data[category])
    print("   -> 多言語翻訳および3行要約完了。")

    print("🧠 [Step 2] Sam Altman & Executive Board (Analysts): 情報を総合解析し、Antigravityの戦略をディベートしています...")
    analysis_result = analyze_trends(all_data)
    print("   -> 戦略分析完了。")

    print("📊 [Step 3] E. Tufte & D. Ogilvy (Publisher): 拡張エグゼクティブレポートを生成しています...")
    report_path = generate_daily_briefing(analysis_result, all_data)
    print(f"   -> レポート生成完了: {report_path}")

    import subprocess
    from datetime import datetime

    print("🌍 [Step 4] Linus Torvalds (Version Control): ニュースレポートをGitHubへ公開しています...")
    try:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        today_str = datetime.now().strftime('%Y-%m-%d')
 
        # Git コマンドを実行して自動コミットとプッシュ
        # Git操作の基準ディレクトリをプロジェクトルート(base_dir)に変更
        subprocess.run(['git', 'add', '.'], cwd=base_dir, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', f'docs: Auto-publish daily briefing {today_str}'], cwd=base_dir, check=False, capture_output=True)
        subprocess.run(['git', 'push', 'origin', 'main'], cwd=base_dir, check=True, capture_output=True)

        print("   -> GitHubへの自動デプロイ（公開）完了。")
    except Exception as e:
        print(f"   -> [エラー] GitHubへの公開に失敗しました: {e}")

    print("\n✨ The Autonomous Office (v2) routine completed successfully.")

if __name__ == "__main__":
    run_autonomous_office()
