from discord import app_commands, Interaction
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load secrets from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

DEVELOPMENT = True
GUILD_ID = 1207784913609302056

# Minimal intents for slash commands
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Slash command /hello
@bot.tree.command(name="hello", description="Say hi to Ignis")
async def hello(interaction: Interaction):
    await interaction.response.send_message("👋 I’m alive and ready to study!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    if DEVELOPMENT:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"Commands synced to guild {GUILD_ID}: {[cmd.name for cmd in synced]}")
    else:
        synced = await bot.tree.sync()
        print(f"Global commands synced: {[cmd.name for cmd in synced]}")

if __name__ == "__main__":
    bot.run(TOKEN)