import os
import time
import requests
from datetime import datetime

API_KEY = os.getenv("FINNHUB_API_KEY")
WEBHOOK_URL = os.getenv("NEWS_WEBHOOK")

if not API_KEY:
    raise ValueError("FINNHUB_API_KEY is missing")

if not WEBHOOK_URL:
    raise ValueError("NEWS_WEBHOOK is missing")

posted_articles = set()

KEYWORDS = [
    "federal reserve",
    "fed",
    "interest rate",
    "inflation",
    "cpi",
    "ppi",
    "recession",
    "economy",
    "tariff",
    "china",
    "taiwan",
    "war",
    "sanctions",
    "opec",
    "oil",
    "ipo",
    "merger",
    "acquisition",
    "buyout",
    "bankruptcy",
    "ceo",
    "offering",
    "nasdaq",
    "s&p",
    "dow",
    "stock market",
    "volatility"
]

WATCHLIST = [
    "HOOD",
    "INTC",
    "DELL",
    "NVDA",
    "AMD",
    "TSLA",
    "PLTR",
    "SOFI",
    "META",
    "AMZN",
    "MSFT",
    "AAPL"
]

def get_category(text):
    text = text.lower()

    if any(x in text for x in [
        "fed",
        "federal reserve",
        "interest rate",
        "inflation",
        "cpi",
        "ppi"
    ]):
        return "🏛️ Federal Reserve"

    if any(x in text for x in [
        "war",
        "china",
        "taiwan",
        "tariff",
        "sanctions"
    ]):
        return "🌎 Geopolitics"

    if "ipo" in text:
        return "🏢 IPO Alert"

    if any(x in text for x in [
        "merger",
        "acquisition",
        "buyout"
    ]):
        return "🤝 M&A Alert"

    return "📰 Market News"

def send_discord(headline, summary, url, source):
    category = get_category(headline + " " + summary)

    embed = {
        "title": "🚨 Trippy Alerts News",
      "description": (
    f"📰 **{headline}**\n\n"
    f"📝 {summary[:200]}..."
),
        "url": url,
        "color": 16753920,
        "fields": [
            {
                "name": "Category",
                "value": category,
                "inline": True
            },
            {
                "name": "Source",
                "value": source,
                "inline": True
            }
        ],
        "footer": {
            "text": f"Trippy Alerts • {datetime.now().strftime('%m/%d/%Y %I:%M %p')}"
        }
    }

    requests.post(
        WEBHOOK_URL,
        json={"embeds": [embed]},
        timeout=15
    )

def check_news():
    url = (
        f"https://finnhub.io/api/v1/news"
        f"?category=general"
        f"&token={API_KEY}"
    )

    response = requests.get(url, timeout=20)

    if response.status_code != 200:
        print(f"Finnhub Error: {response.status_code}")
        return

    articles = response.json()

    for article in articles:

        article_id = str(article.get("id"))

        if article_id in posted_articles:
            continue

        headline = article.get("headline", "")
        summary = article.get("summary", "")
        article_url = article.get("url", "")
        source = article.get("source", "Unknown")

        combined_text = (
            headline + " " + summary
        ).lower()

        keyword_match = any(
            keyword.lower() in combined_text
            for keyword in KEYWORDS
        )

        watchlist_match = any(
            ticker.lower() in combined_text
            for ticker in WATCHLIST
        )

        if keyword_match or watchlist_match:

            send_discord(
                headline,
                summary,
                article_url,
                source
            )

            posted_articles.add(article_id)

            print(f"Posted: {headline}")

            time.sleep(2)

print("🚨 Trippy Alerts News Bot Started")

while True:
    try:
        check_news()
        time.sleep(300)  # 5 minutes

    except Exception as e:
        print(f"ERROR: {e}")
        time.sleep(60)
