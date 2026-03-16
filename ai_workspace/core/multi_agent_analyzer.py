import os
import json
import anthropic

def _get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)

def analyze_trends(all_data):
    """
    サム・アルトマン（The Analysts）によるマルチエージェント分析システム。
    為替、ニュース群(Tech, Japan, Taiwan, AI)を総合的に分析し、
    Antigravityのアクションプランを策定する。
    """
    if not all_data:
        return "No data to analyze today."

    # 分析用プロンプトの構築
    prompt = "以下の最新データに基づき、我々AI開発組織『Antigravity』が次に取るべきアクションを、Steve Jobs(UX視点)、Sam Altman(技術視点)、Jeff Bezos(ビジネス視点)の3人のディベート形式でまとめ、最後にElon Musk(CEO)が今日の全社号令を出してください。\n\n"

    rate = all_data.get('exchange_rate', {}).get('twd_to_jpy', 'N/A')
    prompt += f"■ 【為替】 1 TWD = {rate} JPY\n\n"

    for category, news_list in all_data.items():
        if category == 'exchange_rate' or not news_list: continue
        prompt += f"■ 【{category.upper()}】\n"
        for i, item in enumerate(news_list[:5], 1):
            prompt += f"  - {item['title']}\n"
        prompt += "\n"

    client = _get_client()
    if not client:
        print("Warning: ANTHROPIC_API_KEY is not set. Using simulated offline analysis.")
        return simulate_offline_analysis(all_data)

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system="あなたは30名の専門家からなる最強のAI開発組織『Antigravity』の頭脳です。提示されたニュースと経済指標からインサイトを抽出し、具体的なネクストアクションを立案してください。",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Analyzer Error ([Sam Altman]): API call failed. {e}")
        return simulate_offline_analysis(all_data)


def simulate_offline_analysis(all_data):
    """APIキーがない場合のフォールバック（シミュレーション）"""
    rate = all_data.get('exchange_rate', {}).get('twd_to_jpy', 'N/A')

    analysis = f"## 🤖 Antigravity Multi-Agent Analysis (Offline Simulation)\n\n"
    analysis += f"**Jeff Bezos (Ops)**: 「現在の台湾ドル円レートは {rate} だ。為替変動リスクを考慮しつつ、台湾市場へのハードウェア調達方針を再考すべきだろう。」\n\n"
    analysis += f"**Steve Jobs (Design)**: 「いや、大事なのはユーザー体験だ。日台ニュースの動きを見ると、両国のユーザーはより直感的なAIアシスタント『Antigravity』のコア機能を求めている。」\n\n"
    analysis += f"**Sam Altman (Tech)**: 「Google AntigravityやAI関連の新技術のニュースもある。我々はすぐにこれらのエッセンスを我々のRAG基盤に今日中にテスト組み込みするべきだ。」\n\n"
    analysis += f"**Elon Musk (CEO)**: 「よし、今日の全社アクションプランはこれだ。1. 台湾インフラのコスト最適化設計 2. Google AI最新技術の検証と導入。直ちに取り掛かれ！」\n"
    return analysis


def enhance_news_with_summary(news_list):
    """
    ヨシュア・ベンジオ（NLP担当）とThe Crawlerの連携モジュール。
    リンク先から本文を抽出し、Claude AIを用いて3行程度の日本語要約（Abstract）を作成する。
    """
    import urllib.request
    from bs4 import BeautifulSoup
    import ssl
    import difflib
    import re

    client = _get_client()

    # Claude APIがない場合はdeep-translatorにフォールバック
    translator = None
    if not client:
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source='auto', target='ja')
        except:
            pass

    context = ssl._create_unverified_context()

    for item in news_list:
        link = item.get('link', '')
        original_title = item.get('title', '')
        fallback_summary = item.get('summary', '')

        # 1. 実際の記事本文のスクレイピング試行
        article_text = ""
        if link:
            try:
                req = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req, context=context, timeout=5) as response:
                    html_buf = response.read().decode('utf-8', errors='ignore')

                real_url = link
                m = re.search(r'URL=([^"]+)"', html_buf)
                if m:
                    real_url = m.group(1)
                elif '<a href="' in html_buf:
                    soup = BeautifulSoup(html_buf, 'html.parser')
                    a_tag = soup.find('a')
                    if a_tag and a_tag.has_attr('href') and 'http' in a_tag['href']:
                        real_url = a_tag['href']

                if real_url != link:
                    req2 = urllib.request.Request(real_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
                    with urllib.request.urlopen(req2, context=context, timeout=5) as response2:
                        html_buf = response2.read().decode('utf-8', errors='ignore')

                soup = BeautifulSoup(html_buf, 'html.parser')
                paragraphs = soup.find_all('p')
                article_text = " ".join([p.get_text() for p in paragraphs])
                article_text = re.sub(r'\s+', ' ', article_text).strip()[:1500]
            except Exception:
                pass

        # タイトルとの重複チェック
        sim = difflib.SequenceMatcher(None, original_title[:50], fallback_summary[:50]).ratio()
        if sim > 0.6 or len(fallback_summary) < 20 or "Google ニュースですべての記事を見る" in fallback_summary:
            fallback_summary = ""

        text_to_summarize = article_text if len(article_text) > 80 else fallback_summary

        # DuckDuckGo再検索フォールバック
        if len(text_to_summarize) < 80:
            try:
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    results = list(ddgs.text(original_title, max_results=3))
                    if results:
                        snippets = [r.get('body', '') for r in results]
                        text_to_summarize = " ".join(snippets)
                    else:
                        text_to_summarize = original_title
            except Exception:
                text_to_summarize = original_title

        if client:
            # Claude APIによる完璧な3行要約 + 詳細概要の生成
            prompt = (
                f"以下のニュース記事のタイトルと抽出された本文（または検索スニペット）を読み解き、以下の2つの要素で出力してください。\n\n"
                f"1. 『この記事が全体として何を伝えているか』をとにかく簡潔に【3行程度の日本語の箇条書き（・から始める）】で要約（Abstract）してください。\n"
                f"2. その後、改行してから「【詳細概要】」という見出しをつけ、このニュースの背景、業界や市場への影響、今後の展望などについて、提供された断片的な情報からあなたの高度なインテリジェンスで推論し、250〜400文字程度の詳細な解説を記述してください。単なる要約ではなく、エグゼクティブが意思決定に使える『インサイト』を含めてください。\n\n"
                f"元の言語が英語や中国語等の外国語であっても必ず自然な日本語で出力すること。情報が不足している場合は、前後の文脈から最も合理的な事実関係を推測してまとめてください。\n\n"
                f"タイトル: {original_title}\n本文: {text_to_summarize}"
            )
            try:
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=600,
                    system="あなたは最強のAI開発組織『Antigravity』のシニアエディター兼インテリジェンス分析官です。エグゼクティブ向けにニュースの核心を突く推論に満ちた要約と深い考察を提供します。取得失敗の言い訳は絶対に含めず、常に自信に満ちた分析を提供してください。",
                    messages=[{"role": "user", "content": prompt}]
                )
                item['summary'] = response.content[0].text

                # タイトルも確実に日本語化
                title_response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=100,
                    messages=[{"role": "user", "content": f"以下のニュースタイトルを自然な日本語に翻訳してください。すでに日本語であればそのまま出力してください。翻訳結果のみ出力し、説明は不要です。\n{original_title}"}]
                )
                item['title'] = title_response.content[0].text.strip()

            except Exception as e:
                item['summary'] = f"・要約生成処理中にエラーが発生しました。\n・{e}"

        else:
            # APIキーがない場合のフォールバック（deep-translator）
            if translator:
                try:
                    trans_title = translator.translate(original_title)
                    item['title'] = "[翻訳] " + trans_title

                    trans_text = translator.translate(text_to_summarize[:300])
                    lines = trans_text.split('。')
                    summary_lines = [f"・{line.strip()}。" for line in lines if len(line.strip()) > 5][:3]

                    if summary_lines:
                        item['summary'] = "\n".join(summary_lines)
                    else:
                        item['summary'] = f"・{translator.translate(original_title)}"

                except Exception as e:
                    item['summary'] = f"翻訳エラー: {e}"
            else:
                item['summary'] = text_to_summarize[:200]

    return news_list
