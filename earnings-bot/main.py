import os

print("🚨 EARNINGS BOT STARTED 🚨")
print("TOKEN EXISTS:", os.getenv("BOT_TOKEN") is not None)
print("FMP EXISTS:", os.getenv("FMP_API_KEY") is not None)

import discord
from discord.ext import tasks
import requests
from datetime import datetime, timedelta
import pytzF
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
def get_earnings(from_date, to_date):
    url = "https://financialmodelingprep.com/api/v3/earning_calendar"

    params = {
        "from": from_date,
        "to": to_date,
        "apikey": FMP_API_KEY
    }

    try:
        r = requests.get(url, params=params)

        print("FMP STATUS:", r.status_code)
        print("FMP RESPONSE:", r.text[:300])

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

            earnings = get_earnings(day, day)

            msg = "📊 **TODAY EARNINGS**\n\n"
            msg += "\n".join(earnings) if earnings else "No earnings today."

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

            earnings = get_earnings(start, end)

            msg = "📅 **WEEKLY EARNINGS CALENDAR**\n\n"
            msg += "\n".join(earnings) if earnings else "No earnings next week."

            await channel.send(msg)

            print("WEEKLY SENT")
            last_weekly_run = week_id

        except Exception as e:
            print("WEEKLY TASK ERROR:", e)


# =========================
# RUN BOT
# =========================
client.run(TOKEN)
