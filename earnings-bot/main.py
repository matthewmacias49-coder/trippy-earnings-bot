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


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print(f"Message received: {message.content}")

    if message.content.lower() == "!earnings":

        try:
            url = (
                f"https://financialmodelingprep.com/api/v3/earning_calendar"
                f"?apikey={FMP_API_KEY}"
            )

            response = requests.get(url, timeout=15)
            data = response.json()

            if not data:
                await message.channel.send("❌ No earnings data returned.")
                return

            msg = "📅 **UPCOMING EARNINGS**\n\n"

            count = 0

            for item in data:
                symbol = item.get("symbol", "N/A")
                date = item.get("date", "N/A")
                time = item.get("time", "")

                if time == "amc":
                    session = "PM"
                elif time == "bmo":
                    session = "AM"
                else:
                    session = "?"

                msg += f"🔥 {symbol} - {date} ({session})\n"

                count += 1

                if count >= 10:
                    break

            await message.channel.send(msg)

        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")


client.run(TOKEN)
