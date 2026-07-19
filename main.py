import discord
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")
    await client.change_presence(
        activity=discord.Game(name="Building my first bot 🚀")
    )

client.run(TOKEN)