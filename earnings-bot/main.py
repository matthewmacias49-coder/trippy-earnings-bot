import discord
from discord.ext import tasks
import os

TOKEN = os.getenv("BOT_TOKEN")

EARNINGS_CHANNEL_ID = 1511454316588826754

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print("BOT READY TRIGGERED:", client.user)

    # start loop
    if not earnings_post.is_running():
        earnings_post.start()
        print("TASK STARTED")


@tasks.loop(seconds=30)  # 30 sec test interval (change later)
async def earnings_post():
    print("LOOP RUNNING")

    channel = client.get_channel(EARNINGS_CHANNEL_ID)

    print("CHANNEL FOUND:", channel)

    if channel is None:
        print("ERROR: Channel is None (bot can't access it)")
        return

    try:
        await channel.send("📊 Earnings bot is working!")
        print("MESSAGE SENT")
    except Exception as e:
        print("SEND ERROR:", e)


client.run(TOKEN)
