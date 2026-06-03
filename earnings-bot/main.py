import discord
from discord.ext import tasks
import os
import yfinance as yf
from datetime import datetime, timedelta

TOKEN = os.getenv("BOT_TOKEN")

EARNINGS_CHANNEL_ID = 1511454316588826754

intents = discord.Intents.default()
client = discord.Client(intents=intents)


# ---------- REAL EARNINGS FUNCTION ----------
def get_earnings():
    tickers = [
        "AAPL", "MSFT", "NVDA", "TSLA", "AMZN",
        "META", "AMD", "GOOGL", "NFLX", "PLTR"
    ]

    results = []
    today = datetime.now().date()
    end = today + timedelta(days=7)

    for t in tickers:
        try:
            stock = yf.Ticker(t)
            cal = stock.calendar

            if cal is not None and not cal.empty:
                earnings_date = cal.iloc[0, 0]

                if isinstance(earnings_date, str):
                    earnings_date = datetime.strptime(
                        earnings_date.split(" ")[0],
                        "%Y-%m-%d"
                    ).date()

                if today <= earnings_date <= end:
                    results.append(f"🔥 {t} — {earnings_date}")

        except Exception as e:
            print(f"{t} error: {e}")

    return results


# ---------- READY ----------
@client.event
async def on_ready():
    print("BOT READY TRIGGERED:", client.user)

    if not earnings_post.is_running():
        earnings_post.start()
        print("TASK STARTED")


# ---------- LOOP ----------
@tasks.loop(hours=24)  # daily post (change to 30 sec if testing)
async def earnings_post():
    print("FETCHING REAL EARNINGS...")

    channel = client.get_channel(EARNINGS_CHANNEL_ID)

    print("CHANNEL FOUND:", channel)

    if channel is None:
        print("ERROR: Channel is None")
        return

    earnings = get_earnings()

    if not earnings:
        message = "📊 No major earnings in next 7 days (tracked stocks)."
    else:
        message = "📊 **REAL EARNINGS CALENDAR (NEXT 7 DAYS)**\n\n" + "\n".join(earnings)

    try:
        await channel.send(message)
        print("MESSAGE SENT")
    except Exception as e:
        print("SEND ERROR:", e)


client.run(TOKEN)
