import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

LOG_CHANNEL_NAME = "message-logs"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    await bot.change_presence(
        activity=discord.Game(name="Building my first bot 🚀")
    )

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands!")
    except Exception as e:
        print(e)

def get_log_channel(guild):
    return discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)

@bot.event
async def on_message_delete(message):
    if message.author.bot or message.guild is None:
        return

    channel = get_log_channel(message.guild)
    if channel:
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.red()
        )
        embed.add_field(name="Author", value=message.author.mention, inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        embed.add_field(name="Content", value=message.content or "*No text*", inline=False)
        await channel.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.guild is None:
        return

    if before.content == after.content:
        return

    channel = get_log_channel(before.guild)
    if channel:
        embed = discord.Embed(
            title="✏️ Message Edited",
            color=discord.Color.orange()
        )
        embed.add_field(name="Author", value=before.author.mention, inline=False)
        embed.add_field(name="Channel", value=before.channel.mention, inline=False)
        embed.add_field(name="Before", value=before.content or "*No text*", inline=False)
        embed.add_field(name="After", value=after.content or "*No text*", inline=False)
        await channel.send(embed=embed)

# !ping
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

# /ping
@bot.tree.command(name="ping", description="Check if the bot is online.")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# !hello
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.mention}! 👋")

# /hello
@bot.tree.command(name="hello", description="Say hello.")
async def slash_hello(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Hello, {interaction.user.mention}! 👋"
    )

@bot.event
async def on_message(message):
    await bot.process_commands(message)

bot.run(TOKEN)