import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import ssl
import html
import re

def fetch_exchange_rate():
    """TWD/JPYのリアルタイム為替レートをパブリックAPIから取得"""
    url = "https://api.exchangerate-api.com/v4/latest/TWD"
    context = ssl._create_unverified_context()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context) as response:
            data = json.loads(response.read().decode('utf-8'))
            twd_to_jpy = data.get('rates', {}).get('JPY', 0.0)
            return {"twd_to_jpy": twd_to_jpy, "status": "ok"}
    except Exception as e:
        print(f"Exchange Rate Error: {e}")
        return {"twd_to_jpy": "N/A", "status": "error"}

def fetch_rss_news(url, limit=5):
    """汎用RSS(Google News等)取得関数"""
    context = ssl._create_unverified_context()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)
        items = root.findall(".//item")

        extracted = []
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") is not None else "No Title"
            link = item.find("link").text if item.find("link") is not None else "No Link"
            description = item.find("description").text if item.find("description") is not None else ""

            # HTMLタグ等が含まれる場合は徹底的にクリーンアップ
            clean_summary = re.sub(r'<[^>]+>', '', description)
            clean_summary = html.unescape(clean_summary)
            clean_summary = re.sub(r'\s+', ' ', clean_summary).strip()

            extracted.append({
                "title": title,
                "link": link,
                "summary": clean_summary[:200] + "..." if len(clean_summary) > 200 else clean_summary
            })
        return extracted
    except Exception as e:
        print(f"RSS Fetch Error for {url}: {e}")
        return []

def run_all_crawlers():
    """全ての情報を一括収集するメインクローラー"""
    print("Collecting Exchange Rates...")
    rate_info = fetch_exchange_rate()

    # 従来通りのTechTrend（HackerNews）
    print("Collecting Hacker News (Global Tech)...")
    tech_news = fetch_rss_news("https://news.ycombinator.com/rss", limit=5)

    # 日本のGoogle News トピック
    print("Collecting Japan News...")
    jp_news = fetch_rss_news("https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja", limit=5)

    # 台湾のニュース（中国語・現地の生データを取得。後段でAIが翻訳する）
    print("Collecting Taiwan & China Relation News (Raw Chinese)...")
    tw_query = urllib.parse.quote("台灣 中國")
    tw_news = fetch_rss_news(f"https://news.google.com/rss/search?q={tw_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant", limit=5)

    # Google Antigravity / AI関連技術
    print("Collecting Google AI & Antigravity News...")
    ai_query = urllib.parse.quote("Google Antigravity OR Google AI")
    ai_news = fetch_rss_news(f"https://news.google.com/rss/search?q={ai_query}&hl=ja&gl=JP&ceid=JP:ja", limit=5)

    return {
        "exchange_rate": rate_info,
        "tech_news": tech_news,
        "japan_news": jp_news,
        "taiwan_news": tw_news,
        "ai_news": ai_news
    }

if __name__ == "__main__":
    print("Initializing The Crawler v2...")
    all_data = run_all_crawlers()
    print(json.dumps(all_data, indent=2, ensure_ascii=False))
