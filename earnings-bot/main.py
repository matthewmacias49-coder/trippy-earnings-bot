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
    "AAPL", "MSFT", "NVDA", "AMZN", "META",
    "GOOGL", "TSLA", "AMD", "AVGO", "NFLX",
    "PLTR", "HOOD", "INTC", "DELL", "ARM",
    "SMCI", "COIN", "UBER", "CRM", "ORCL",
    "QCOM", "SNOW", "SHOP", "RBLX", "PYPL",
    "JPM", "BAC", "GS", "WMT", "COST",
    "LLY", "UNH", "XOM", "CVX", "COP"
]

TIER_2 = [
    "ADBE", "AMAT", "MU", "PANW", "CRWD",
    "ANET", "MRVL", "SNPS", "KLAC", "LRCX",
    "ADI", "MCHP", "NXPI", "ON", "ASML",
    "TTD", "DDOG", "ZS", "NET", "MDB",
    "TEAM", "HUBS", "DOCU", "OKTA",
    "ABNB", "BKNG", "EXPE",
    "DIS", "CMCSA", "PARA", "WBD",
    "KO", "PEP", "MCD", "SBUX", "NKE",
    "HD", "LOW", "TGT",
    "CAT", "DE", "GE", "RTX",
    "LMT", "BA",
    "UPS", "FDX",
    "PFE", "MRK", "ABBV", "JNJ",
    "ISRG", "TMO", "DHR",
    "SCHW", "BLK", "MS", "C", "AXP",
    "SPGI", "CME",
    "FCX", "NEM", "SLB", "EOG", "MPC"
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
@client.event
async def on_ready():
    print("BOT READY TRIGGERED:", client.user)

    try:
        channel = await client.fetch_channel(CHANNEL_ID)
        await channel.send("🟢 Trippy Alerts online")
        print("ONLINE MESSAGE SENT")

    except Exception as e:
        print("ON_READY ERROR:", e)

    try:
        if not today_task.is_running():
            today_task.start()
            print("DAILY TASK STARTED")

        print("today_task running:", today_task.is_running())

        if not weekly_task.is_running():
            weekly_task.start()
            print("WEEKLY TASK STARTED")

        print("weekly_task running:", weekly_task.is_running())

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

tier1, tier2 = get_earnings(day, day)

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
# RUN BOT
# =========================
client.run(TOKEN)
