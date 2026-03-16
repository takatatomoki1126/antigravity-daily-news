import os
import json
from openai import OpenAI

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

    # データのパース
    rate = all_data.get('exchange_rate', {}).get('twd_to_jpy', 'N/A')
    prompt += f"■ 【為替】 1 TWD = {rate} JPY\n\n"

    for category, news_list in all_data.items():
        if category == 'exchange_rate' or not news_list: continue
        prompt += f"■ 【{category.upper()}】\n"
        for i, item in enumerate(news_list[:3], 1): # トークン節約のため各3件
            prompt += f"  - {item['title']}\n"
        prompt += "\n"

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY is not set. Using simulated offline analysis.")
        return simulate_offline_analysis(all_data)

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは30名の専門家からなる最強のAI開発組織『Antigravity』の頭脳です。提示されたニュースと経済指標からインサイトを抽出し、具体的なネクストアクションを立案してください。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
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
    リンク先から本文を抽出し、AI（または翻訳エンジン）を用いて3行程度の日本語要約（Abstract）を作成する。
    """
    import urllib.request
    from bs4 import BeautifulSoup
    import ssl
    import time

    api_key = os.environ.get("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key) if api_key else None

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
                import re
                req = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req, context=context, timeout=5) as response:
                    html_buf = response.read().decode('utf-8', errors='ignore')

                # Google NewsのJS/Metaリダイレクトを処理して本当のURLへ飛ぶ
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
                # <p>タグからテキスト抽出して連結
                paragraphs = soup.find_all('p')
                article_text = " ".join([p.get_text() for p in paragraphs])
                article_text = re.sub(r'\s+', ' ', article_text).strip()[:1500]
            except Exception as e:
                pass

        # タイトルとの重複チェック（RSS特有の「概要がタイトルそのまま」問題を弾く）
        import difflib
        sim = difflib.SequenceMatcher(None, original_title[:50], fallback_summary[:50]).ratio()
        if sim > 0.6 or len(fallback_summary) < 20 or "Google ニュースですべての記事を見る" in fallback_summary:
            fallback_summary = "（本文のスクレイピングに失敗したため、詳細な要約を生成できませんでした。元記事のリンクから直接内容を参照してください）"

        # 取得できなければRSSの要約（fallback）を使用
        text_to_summarize = article_text if len(article_text) > 80 else fallback_summary

        # === 敗北宣言（取得失敗）の禁止：第一原理に基づくDuckDuckGo再検索フォールバック ===
        if "詳細な要約を生成できません" in text_to_summarize or len(text_to_summarize) < 80:
            try:
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    # ニュースタイトルでWeb検索を行い、スニペットをかき集める
                    results = list(ddgs.text(original_title, max_results=3))
                    if results:
                        snippets = [r.get('body', '') for r in results]
                        text_to_summarize = " ".join(snippets)
                    else:
                        text_to_summarize = f"{original_title}"
            except Exception as e:
                text_to_summarize = f"{original_title}"

        if client:
            # APIキーがある場合はLLMによる完璧な3行要約 + 詳細概要の生成
            prompt = f"以下のニュース記事のタイトルと抽出された本文（または検索スニペット）を読み解き、以下の2つの要素で出力してください。\n\n" \
                     f"1. 『この記事が全体として何を伝えているか』をとにかく簡潔に【3行程度の日本語の箇条書き（・から始める）】で要約（Abstract）してください。\n" \
                     f"2. その後、改行してから「【詳細概要】」という見出しをつけ、このニュースの背景、業界や市場への影響、今後の展望などについて、推論を交えた200〜300文字程度の詳細な解説を記述してください。\n\n" \
                     f"元の言語が英語や中国語等の外国語であっても必ず自然な日本語で出力すること。もし提供されたスニペットが断片的である場合は、あなたの持つ高度な知見と推論能力で前後の文脈を推測して事実をまとめてください。\n\n" \
                     f"タイトル: {original_title}\n本文: {text_to_summarize}"
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "あなたは優秀なシニアエディター兼インテリジェンス分析官です。エグゼクティブ向けにニュースの核心を突く推論に満ちた要約と深い考察を提供します。取得失敗の言い訳は絶対に含めないでください。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.4
                )
                item['summary'] = response.choices[0].message.content

                # タイトルも確実に日本語化
                title_prompt = f"以下のニュースタイトルを自然な日本語に翻訳してください。すでに日本語であればそのまま出力してください。\n{original_title}"
                title_res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": title_prompt}],
                    temperature=0.1
                )
                item['title'] = title_res.choices[0].message.content.strip()

            except Exception as e:
                item['summary'] = f"・要約生成処理中にLLMとの通信エラーが発生しました。\n・{e}"
        else:
            # APIキーがない（ローカル動作）の場合の無料シミュレーション（deep-translator）
            offline_notice = "\n\n【詳細概要】\n(現在OPENAI_API_KEYが未設定のため、オフラインモードでの代替処理が実行されています。AIによる詳細な背景分析や推論インサイトを生成するには、システム環境変数にAPIキーを指定してください。)"
            if translator:
                try:
                    trans_title = translator.translate(original_title)
                    item['title'] = "[翻訳] " + trans_title

                    # 本文(または検索スニペット)の翻訳
                    trans_text = translator.translate(text_to_summarize[:300])
                    lines = trans_text.split('。')
                    summary_lines = [f"・{line.strip()}。" for line in lines if len(line.strip()) > 5][:3]

                    if not summary_lines:
                        simulated_summary = translator.translate(original_title)
                        item['summary'] = f"・{simulated_summary}" + offline_notice
                    else:
                        item['summary'] = "\n".join(summary_lines) + offline_notice

                except Exception as e:
                    item['summary'] = f"翻訳エラー: {e}" + offline_notice
            else:
                item['summary'] = text_to_summarize[:200] + offline_notice

    return news_list
