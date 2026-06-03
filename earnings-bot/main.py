import discord
import os

TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    print("BOT READY")

@client.event
async def on_message(message):
    print(f"SAW MESSAGE: {message.content}")

    if message.author.bot:
        return

    await message.channel.send("I SAW YOUR MESSAGE")

client.run(TOKEN)
