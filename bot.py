from discord import app_commands, Interaction
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# dev toggle
DEVELOPMENT = False
GUILD_ID = 1207784913609302056

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# test command /hello
@bot.tree.command(name="hello", description="Say hi to Ignis")
async def hello(interaction: Interaction):
    await interaction.response.send_message("👋 I’m alive and ready to study!")

# bot event for when the bot is logged in and ready
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

# runs code if the file is run directly
if __name__ == "__main__":
    bot.run(TOKEN)