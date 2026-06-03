import discord
from discord.ext import tasks
import os
import requests
from datetime import datetime, timedelta
import pytz

# =========================
# ENV VARS
# =========================
TOKEN = os.getenv("BOT_TOKEN")
FMP_API_KEY = os.getenv("FMP_API_KEY")

EARNINGS_CHANNEL_ID = 1511454316588826754

intents = discord.Intents.default()
client = discord.Client(intents=intents)

PST = pytz.timezone("US/Pacific")


# =========================
# FMP EARNINGS FUNCTION
# =========================
def get_earnings(from_date, to_date):
    url = "https://financialmodelingprep.com/api/v3/earning_calendar"

    params = {
        "from": from_date,
        "to": to_date,
        "apikey": FMP_API_KEY
    }

    try:
        r = requests.get(url, params=params)
        data = r.json()

        results = []

        for item in data:
            symbol = item.get("symbol")
            date = item.get("date")

            if symbol and date:
                results.append(f"🔥 {symbol} — {date}")

        return results

    except Exception as e:
        print("FMP ERROR:", e)
        return []


# =========================
# READY EVENT
# =========================
@client.event
async def on_ready():
    print("BOT READY:", client.user)

    # 🧪 TEST RUN ON START (VERY IMPORTANT)
    await test_run()

    today_task.start()
    weekly_task.start()


# =========================
# TEST FUNCTION
# =========================
async def test_run():
    channel = client.get_channel(EARNINGS_CHANNEL_ID)

    if not channel:
        print("Channel not found for test")
        return

    today = datetime.now(PST).date().strftime("%Y-%m-%d")

    earnings = get_earnings(today, today)

    if not earnings:
        msg = "🧪 **TEST RUN**\n\nNo earnings today (or API empty)."
    else:
        msg = "🧪 **TEST RUN - TODAY EARNINGS**\n\n" + "\n".join(earnings)

    await channel.send(msg)
    print("TEST MESSAGE SENT")


# =========================
# 6AM PST MON–FRI
# =========================
@tasks.loop(minutes=1)
async def today_task():
    now = datetime.now(PST)

    if now.weekday() >= 5:
        return

    if now.hour == 6 and now.minute == 0:

        channel = client.get_channel(EARNINGS_CHANNEL_ID)
        if not channel:
            print("Channel not found")
            return

        today = now.date().strftime("%Y-%m-%d")

        earnings = get_earnings(today, today)

        if not earnings:
            msg = "📊 **TODAY EARNINGS**\n\nNo earnings today."
        else:
            msg = "📊 **TODAY EARNINGS (6AM PST)**\n\n" + "\n".join(earnings)

        await channel.send(msg)
        print("6AM earnings posted")


# =========================
# SUNDAY 5PM PST
# =========================
@tasks.loop(minutes=1)
async def weekly_task():
    now = datetime.now(PST)

    if now.weekday() != 6:
        return

    if now.hour == 17 and now.minute == 0:

        channel = client.get_channel(EARNINGS_CHANNEL_ID)
        if not channel:
            print("Channel not found")
            return

        start = now.date().strftime("%Y-%m-%d")
        end = (now.date() + timedelta(days=7)).strftime("%Y-%m-%d")

        earnings = get_earnings(start, end)

        if not earnings:
            msg = "📅 **WEEKLY EARNINGS CALENDAR**\n\nNo earnings next week."
        else:
            msg = "📅 **WEEKLY EARNINGS CALENDAR (FMP)**\n\n" + "\n".join(earnings)

        await channel.send(msg)
        print("Weekly earnings posted")


# =========================
# START BOT
# =========================
client.run(TOKEN)
