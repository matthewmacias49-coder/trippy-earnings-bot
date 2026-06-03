import discord
from discord.ext import tasks
import os

TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

EARNINGS_CHANNEL_ID = 1511454316588826754


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    # start your loop (IMPORTANT)
    earnings_post.start()


@tasks.loop(hours=24)  # change timing if you want
async def earnings_post():
    channel = client.get_channel(EARNINGS_CHANNEL_ID)

    if channel is None:
        print("Channel not found — check ID or bot access")
        return

    message = """📊 **EARNINGS WATCHLIST**

🔥 NVDA
🔥 TSLA
🔥 AAPL
🔥 AMD
"""

    await channel.send(message)
    print("Earnings posted!")


client.run(TOKEN)
