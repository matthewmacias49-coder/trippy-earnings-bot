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

# prevents double posting
last_daily_run = None
last_weekly_run = None


# =========================
# FMP EARNINGS
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
# READY
# =========================
@client.event
async def on_ready():
    print("BOT READY:", client.user)

    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("🟢 Trippy Alerts online")

    today_task.start()
    weekly_task.start()


# =========================
# DAILY 6AM PST MON-FRI
# =========================
@tasks.loop(minutes=1)
async def today_task():
    global last_daily_run

    now = datetime.now(PST)

    if now.weekday() >= 5:
        return

    # trigger AFTER 6AM once per day
    if now.hour >= 6:

        day = now.date().isoformat()

        if last_daily_run == day:
            return

        channel = client.get_channel(CHANNEL_ID)
        if not channel:
            print("Channel missing")
            return

        earnings = get_earnings(day, day)

        msg = "📊 **TODAY EARNINGS**\n\n"
        msg += "\n".join(earnings) if earnings else "No earnings today."

        await channel.send(msg)

        print("DAILY SENT")
        last_daily_run = day


# =========================
# SUNDAY 5PM PST WEEKLY
# =========================
@tasks.loop(minutes=1)
async def weekly_task():
    global last_weekly_run

    now = datetime.now(PST)

    if now.weekday() != 6:
        return

    # trigger AFTER 5PM once per week
    if now.hour >= 17:

        week_id = now.strftime("%Y-%U")

        if last_weekly_run == week_id:
            return

        channel = client.get_channel(CHANNEL_ID)
        if not channel:
            print("Channel missing")
            return

        start = now.date().isoformat()
        end = (now.date() + timedelta(days=7)).isoformat()

        earnings = get_earnings(start, end)

        msg = "📅 **WEEKLY EARNINGS CALENDAR**\n\n"
        msg += "\n".join(earnings) if earnings else "No earnings next week."

        await channel.send(msg)

        print("WEEKLY SENT")
        last_weekly_run = week_id


# =========================
# RUN
# =========================
client.run(TOKEN)
