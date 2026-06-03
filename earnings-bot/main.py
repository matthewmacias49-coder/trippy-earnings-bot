import discord
import os
import requests

TOKEN = os.getenv("BOT_TOKEN")
FMP_API_KEY = os.getenv("FMP_API_KEY")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    print("EARNINGS BOT READY")


@client.event
async def on_message(message):
    if message.author.bot:
        return

    print(f"MESSAGE RECEIVED: {message.content}")

    if message.content.lower().strip() == "!earnings":

        await message.channel.send("🔍 Looking up earnings...")

        try:
            url = f"https://financialmodelingprep.com/api/v3/earning_calendar?apikey={FMP_API_KEY}"

            response = requests.get(url, timeout=15)

            print(f"STATUS CODE: {response.status_code}")

            data = response.json()

            if not data:
                await message.channel.send("❌ No earnings data returned.")
                return

            msg = "📅 **UPCOMING EARNINGS**\n\n"

            for item in data[:10]:

                symbol = item.get("symbol", "N/A")
                date = item.get("date", "N/A")
                time = item.get("time", "")

                if time == "bmo":
                    session = "AM"
                elif time == "amc":
                    session = "PM"
                else:
                    session = "?"

                msg += f"🔥 {symbol} - {date} ({session})\n"

            await message.channel.send(msg)

        except Exception as e:
            print(e)
            await message.channel.send(f"❌ Error: {e}")


client.run(TOKEN)
