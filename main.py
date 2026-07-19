import os
import discord
from discord.ext import commands
from discord import app_commands
from openai import OpenAI

TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DELETED_LOG_CHANNEL = "deleted-logs"
EDITED_LOG_CHANNEL = "edited-logs"
CHAT_LOG_CHANNEL = "chat-logs"

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

def get_deleted_log_channel(guild):
    return discord.utils.get(guild.text_channels, name=DELETED_LOG_CHANNEL)

def get_edited_log_channel(guild):
    return discord.utils.get(guild.text_channels, name=EDITED_LOG_CHANNEL)

def get_chat_log_channel(guild):
    return discord.utils.get(guild.text_channels, name=CHAT_LOG_CHANNEL)

@bot.event
async def on_message_delete(message):
    if message.author.bot or message.guild is None:
        return

    channel = get_deleted_log_channel(message.guild)

    if channel:
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.red()
        )

        embed.add_field(name="Author", value=message.author.mention, inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        embed.add_field(name="Content", value=message.content or "*No text*", inline=False)

        if message.attachments:
            embed.add_field(
                name="Attachments",
                value="\n".join(a.url for a in message.attachments),
                inline=False
            )

        await channel.send(embed=embed)


@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.guild is None:
        return

    if before.content == after.content:
        return

    channel = get_edited_log_channel(before.guild)

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

# !server
@bot.command()
async def server(ctx):
    await ctx.send(
        f"🏠 Server: {ctx.guild.name}\n"
        f"👥 Members: {ctx.guild.member_count}"
    )

# /server
@bot.tree.command(name="server", description="Shows server information.")
async def slash_server(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"🏠 Server: {interaction.guild.name}\n"
        f"👥 Members: {interaction.guild.member_count}"
    )

# !userinfo
@bot.command()
async def userinfo(ctx):
    await ctx.send(
        f"👤 User: {ctx.author}\n"
        f"🆔 ID: {ctx.author.id}"
    )

# /userinfo
@bot.tree.command(name="userinfo", description="Shows your user information.")
async def slash_userinfo(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"👤 User: {interaction.user}\n"
        f"🆔 ID: {interaction.user.id}"
    )

# !avatar
@bot.command()
async def avatar(ctx):
    await ctx.send(ctx.author.display_avatar.url)

# /avatar
@bot.tree.command(name="avatar", description="Shows your avatar.")
async def slash_avatar(interaction: discord.Interaction):
    await interaction.response.send_message(
        interaction.user.display_avatar.url
    )

# !botinfo
@bot.command()
async def botinfo(ctx):
    await ctx.send(
        f"🤖 Bot: {bot.user.name}\n"
        f"📡 Ping: {round(bot.latency * 1000)} ms"
    )

# /botinfo
@bot.tree.command(name="botinfo", description="Shows bot information.")
async def slash_botinfo(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"🤖 Bot: {bot.user.name}\n"
        f"📡 Ping: {round(bot.latency * 1000)} ms"
    )

# !say
@bot.command()
async def say(ctx, *, message):
    await ctx.send(message)

# /say
@bot.tree.command(name="say", description="Make the bot repeat a message.")
@app_commands.describe(message="The message for the bot to say")
async def slash_say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

# !clear
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 Deleted {amount} messages.")
    await msg.delete(delay=5)

# /clear
@bot.tree.command(name="clear", description="Delete messages from the current channel.")
@app_commands.describe(amount="Number of messages to delete")
async def slash_clear(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.",
            ephemeral=True
        )
        return

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(
        f"🧹 Deleted {amount} messages.",
        ephemeral=True
    )

# /chat
@bot.tree.command(name="chat", description="Talk with ChatGPT")
@app_commands.describe(prompt="Ask anything")
async def chat(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()

    try:
        response = client.chat.completions.create(
        model="gpt-4-mini"",
            messages=[{"role": "user", "content": prompt}] 
        )

        await interaction.followup.send(response.choices[0].message.content)

    except Exception as e:
        await interaction.followup.send(f"❌ AI Error:\n{e}")

@bot.event
async def on_message(message):
    if message.author.bot or message.guild is None:
        return

    log_channel = get_chat_log_channel(message.guild)

    if log_channel:
        embed = discord.Embed(
            title="💬 Message Sent",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Author",
            value=f"{message.author.mention} (`{message.author}`)",
            inline=False
        )

        embed.add_field(
            name="Channel",
            value=message.channel.mention,
            inline=False
        )

        embed.add_field(
            name="Message",
            value=message.content or "*No text*",
            inline=False
        )

        if message.attachments:
            embed.add_field(
                name="Attachments",
                value="\n".join(a.url for a in message.attachments),
                inline=False
            )

        await log_channel.send(embed=embed)

    await bot.process_commands(message)

bot.run(TOKEN)

