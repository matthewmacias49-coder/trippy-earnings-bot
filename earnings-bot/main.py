import os

print("🚨 EARNINGS BOT STARTED 🚨")
print("TOKEN EXISTS:", os.getenv("BOT_TOKEN") is not None)
print("FMP EXISTS:", os.getenv("FMP_API_KEY") is not None)

import discord
from discord.ext import tasks
import os
import requests
from datetime import datetime, timedelta
import pytz
# =========================
# ENV
# =========================
TOKEN = os.getenv("BOT_TOKEN")
FMP_API_KEY = os.getenv("FMP_API_KEY")

CHANNEL_ID = 1511454316588826754
NEWS_CHANNEL_ID = 1512534078300094626
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

posted_news = set()
intents = discord.Intents.default()
client = discord.Client(intents=intents)

PST = pytz.timezone("US/Pacific")

# prevent double posts
last_daily_run = None
last_weekly_run = None


# =========================
# FMP EARNINGS API
# =========================
TIER_1 = [
    "AAPL","MSFT","NVDA","AMZN","META",
    "GOOGL","TSLA","AMD","AVGO","NFLX",
    "PLTR","HOOD","INTC","DELL","ARM",
    "SMCI","COIN","UBER","CRM","ORCL",
    "QCOM","SNOW","SHOP","RBLX","PYPL",
    "JPM","BAC","GS","WMT","COST",
    "LLY","UNH","XOM","CVX","COP",

    "ADBE","PANW","CRWD","MU","AMAT",
    "LRCX","MRVL","ABNB","BKNG","ISRG",
    "CAT","RTX","MCD","SBUX","ANET",
    "SNPS","CDNS","MSTR","DASH"
]

TIER_2 = [
    "TJX","ROST","BURL","ULTA","DG","DLTR","FIVE",
    "BBY","GME","KSS","M","JWN","GPS","AEO","ANF",

    "WING","CMG","YUM","DPZ","QSR","SHAK","CAVA",
    "DRI","TXRH","CAKE","BJRI","DENN","JACK","PLAY",
    "MCD","SBUX",

    "KR","ACI","SFM","CAG","GIS","KHC","CPB","HRL",
    "MKC","MDLZ","HSY","STZ",

    "VRTX","REGN","BIIB","BMY","GILD","AMGN","CVS",
    "ELV","HUM","CI","DGX","LH","HCA","UHS",
    "ZBH","SYK","BSX","EW","ALGN",
    "MRK","ABBV","NVO","ISRG",

    "APP","APPS","IOT","SOUN","AI","BBAI","CFLT",
    "ESTC","GTLB","PATH","FSLY","AKAM","UPST",
    "AFRM","SOFI","LC","RKLB","ASTS","LUNR",
    "IONQ","RGTI","QBTS","TEM","HIMS",
    "NBIS","ANET","SNPS","CDNS","SERV","APLD",

    "S","TENB","CYBR","RPD","VRNS","FTNT","SAIL",
    "PANW","CRWD","ZS","NET","DDOG","MDB","OKTA",

    "MPWR","ENTG","ONTO","ALAB","FORM","WOLF",
    "COHR","IPGP","CAMT","ACLS","AEHR",
    "AMAT","MU","ADI","TXN","MRVL","KLAC","LRCX","MCHP",

    "WDAY","NOW","INTU","CDNS","TTWO","EA",
    "U","APPF","PAYC","BILL","TOST","MNDY",
    "DUOL",

    "CELH","ALLY","COF","DFS","RF",
    "HBAN","FITB","KEY","PNC","USB","TROW",
    "BEN","AMP","FIS","FI","GPN",

    "URI","FAST","GWW","PCAR",
    "PWR","ETN","HWM","IR","JCI","ROK",
    "PH","EMR","CAT",

    "OXY","DVN","FANG","APA",
    "BKR","HAL","VLO","PSX","KMI","WMB","SLB","MPC",

    "UAL","DAL","AAL","LUV","ALK",
    "MAR","HLT","RCL","CCL","NCLH",
    "ABNB","BKNG","EXPE",

    "TMUS","VZ","T","CHTR","DISH","SPOT",
    "ROKU","SNAP","PINS","DASH","LYFT",

    "RIVN","LCID","NIO","XPEV","LI",
    "F","GM","STLA",

    "CROX","ONON","DECK","SKX","LULU",
    "ELF","COTY","RL","NKE",

    "JOBY","ACHR","PLUG","BE","RUN","SEDG",
    "ENPH","CHPT","QS","OPEN","RDFN",

    "EXAS","RXRX","CRSP","NTLA",

    "LMT","RTX","NOC","GD","BA","AVAV","KTOS",

    "FCX","NEM","AA","CLF","MP",

    "PLD","O","SPG","EQIX","DLR"
]

WATCHLIST = set(TIER_1 + TIER_2)


def get_earnings(from_date, to_date):
    url = "https://financialmodelingprep.com/stable/earnings-calendar"

    params = {
        "from": from_date,
        "to": to_date,
        "apikey": FMP_API_KEY
    }

    try:
        r = requests.get(url, params=params, timeout=15)

        print("FMP STATUS:", r.status_code)
        print("FMP RESPONSE:", r.text[:500])

        data = r.json()

        # FMP sometimes returns an error dict/string instead of a list
        if not isinstance(data, list):
            print("FMP ERROR RESPONSE:", data)
            return [], []

        tier1 = []
        tier2 = []

        for item in data:

            if not isinstance(item, dict):
                continue

            symbol = item.get("symbol")

            if symbol in TIER_1:
                tier1.append(symbol)

            elif symbol in TIER_2:
                tier2.append(symbol)

        tier1 = sorted(list(set(tier1)))
        tier2 = sorted(list(set(tier2)))

        return tier1, tier2

    except Exception as e:
        print("FMP ERROR:", e)
        return [], []
# =========================
# READY (FIXED + SAFE)
# =========================

@client.event
async def on_ready():
    print("BOT READY TRIGGERED:", client.user)

    try:
        if not today_task.is_running():
            today_task.start()
            print("DAILY TASK STARTED")

        if not weekly_task.is_running():
            weekly_task.start()
            print("WEEKLY TASK STARTED")

        if not news_task.is_running():
            news_task.start()
            print("NEWS TASK STARTED")

    except Exception as e:
        print("TASK START ERROR:", e)

# =========================
# DAILY 6AM PST MON-FRI
# =========================
@tasks.loop(minutes=1)
async def today_task():
    global last_daily_run

    now = datetime.now(PST)

    if now.weekday() >= 5:
        return

    if now.hour >= 6:

        day = now.date().isoformat()

        if last_daily_run == day:
            return

        try:
            channel = await client.fetch_channel(CHANNEL_ID)

start = now.date().isoformat()
end = (now.date() + timedelta(days=1)).isoformat()

tier1, tier2 = get_earnings(start, end)

            msg = "📊 **TODAY'S EARNINGS**\n\n"

            if tier1:
                msg += "🔥 **Tier 1**\n"
                msg += "\n".join(f"• {ticker}" for ticker in tier1)
                msg += "\n\n"

            if tier2:
                msg += "📈 **Tier 2**\n"
                msg += "\n".join(f"• {ticker}" for ticker in tier2)

            if not tier1 and not tier2:
                msg += "No watchlist earnings today."

            await channel.send(msg)

            print("DAILY SENT")
            last_daily_run = day

        except Exception as e:
            print("DAILY TASK ERROR:", e)
            print("DAILY TASK ERROR:", e)


# =========================
# WEEKLY SUNDAY 5PM PST
# =========================
@tasks.loop(minutes=1)
async def weekly_task():
    global last_weekly_run

    now = datetime.now(PST)

    if now.weekday() != 6:
        return

    if now.hour >= 17:

        week_id = now.strftime("%Y-%U")

        if last_weekly_run == week_id:
            return

        try:
            channel = await client.fetch_channel(CHANNEL_ID)

            start = now.date().isoformat()
            end = (now.date() + timedelta(days=7)).isoformat()

            tier1, tier2 = get_earnings(start, end)

            msg = "📅 **WEEKLY EARNINGS CALENDAR**\n\n"

            if tier1:
                msg += "🔥 **Tier 1**\n"
                msg += "\n".join(f"• {ticker}" for ticker in tier1)
                msg += "\n\n"

            if tier2:
                msg += "📈 **Tier 2**\n"
                msg += "\n".join(f"• {ticker}" for ticker in tier2)

            if not tier1 and not tier2:
                msg += "No watchlist earnings next week."

            await channel.send(msg)

            print("WEEKLY SENT")
            last_weekly_run = week_id

        except Exception as e:
            print("WEEKLY TASK ERROR:", e)
# =========================
# BREAKING NEWS
# =========================

# =========================
# MARKET MOVING NEWS FILTER
# =========================

NEWS_KEYWORDS = [

    # FED / ECONOMY
    "federal reserve",
    "fed",
    "powell",
    "interest rate",
    "rate cut",
    "rate hike",
    "inflation",
    "cpi",
    "ppi",
    "pce",
    "nonfarm payroll",
    "jobs report",
    "unemployment",
    "gdp",
    "retail sales",
    "consumer confidence",
    "recession",

    # GOVERNMENT
    "tariff",
    "sanctions",
    "debt ceiling",
    "government shutdown",

    # ENERGY
    "oil",
    "crude",
    "opec",
    "strait of hormuz",
    "iran",
    "saudi arabia",

    # COMPANY EVENTS
    "earnings",
    "guidance",
    "forecast",
    "revenue",
    "profit",
    "ceo",
    "acquisition",
    "merger",
    "buyback",

    # MARKET EVENTS
    "nasdaq",
    "s&p 500",
    "dow jones",
    "spy",
    "qqq"
]

BANNED_WORDS = [

    # foreign markets
    "pakistan",
    "taiwan dollar",
    "taiwan currency",
    "japan inflation",
    "european markets",
    "asian markets",
    "hong kong",
    "singapore",
    "indonesia",
    "philippines",
    "thailand",
    "malaysia",
    "south korea",

    # garbage articles
    "analyst says",
    "analysts say",
    "expert says",
    "experts say",
    "opinion",
    "column",
    "commentary",
    "market wrap",
    "daily roundup",
    "week ahead",
    "stocks to buy",
    "stocks to watch",
    "price target",

    # crypto
    "bitcoin",
    "ethereum",
    "crypto",
    "cryptocurrency",

    # random stuff
    "soccer",
    "nba",
    "nfl",
    "entertainment",
    "celebrity"
]

@tasks.loop(minutes=2)
async def news_task():

    try:
        url = (
            f"https://finnhub.io/api/v1/news"
            f"?category=general"
            f"&token={FINNHUB_API_KEY}"
        )

        r = requests.get(url, timeout=5)

        if r.status_code != 200:
            print("NEWS API ERROR:", r.status_code)
            return

        articles = r.json()

        # On startup, mark existing news as seen
        if len(posted_news) == 0:
            for article in articles:
                article_id = str(article.get("id"))
                posted_news.add(article_id)

            print("NEWS CACHE INITIALIZED")
            return

        # Only check newest articles
        articles = articles[:15]

        channel = await client.fetch_channel(NEWS_CHANNEL_ID)

        for article in articles:

            article_id = str(article.get("id"))

            if article_id in posted_news:
                continue

            headline = article.get("headline", "")
            summary = article.get("summary", "")
            source = article.get("source", "Unknown")
            article_url = article.get("url", "")
            image_url = article.get("image", "")

            text = f"{headline} {summary}".lower()

            # Skip garbage news
            if any(word in text for word in BANNED_WORDS):
                posted_news.add(article_id)
                continue

            keyword_match = any(
                word in text
                for word in NEWS_KEYWORDS
            )

            watchlist_match = any(
                ticker.lower() in text
                for ticker in WATCHLIST
            )

            if not keyword_match and not watchlist_match:
                posted_news.add(article_id)
                continue

            description = summary.strip()

            if not description:
                description = "Market-moving news affecting stocks, earnings, economic data, or major macro events."

            description = description.replace("\n", " ")

            if len(description) > 300:
                description = description[:300] + "..."

            impact = ""

            if any(word in text for word in ["iran", "oil", "opec", "crude", "strait of hormuz"]):
                impact = "⛽ Potential impact: Oil & Energy"

            elif any(word in text for word in ["fed", "inflation", "cpi", "ppi", "pce", "interest rate"]):
                impact = "📈 Potential impact: SPY, QQQ, Nasdaq"

            elif "earnings" in text:
                impact = "💰 Potential impact: Earnings Movers"

            elif any(word in text for word in ["tariff", "sanctions"]):
                impact = "🌎 Potential impact: Broad Market"

            if impact:
                description += f"\n\n{impact}"

            embed = discord.Embed(
                title=headline,
                description=description,
                url=article_url,
                color=0xF39C12
            )

            embed.set_author(name="🚨 Market Alert")
            embed.set_footer(text=source)

            if image_url:
                embed.set_image(url=image_url)

            await channel.send(embed=embed)

            posted_news.add(article_id)

            print("NEWS POSTED:", headline)

            break

    except Exception as e:
        print("NEWS TASK ERROR:", e)
# =========================
# START BOT
# =========================

if __name__ == "__main__":
    print("🚀 STARTING DISCORD LOGIN...")
    client.run(TOKEN)
