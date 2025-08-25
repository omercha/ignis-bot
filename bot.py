from discord import app_commands, Interaction
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from utils.openai_api import ask_openai

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# dev toggle
DEVELOPMENT = True
GUILD_ID = 1207784913609302056

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=None, intents=intents)

# test command /hello
@bot.tree.command(name="hello", description="Say hi to Ignis")
async def hello(interaction: Interaction):
    await interaction.response.send_message("👋 I’m alive and ready to study!")

# command /ask
@bot.tree.command(name="ask", description="Ask Ignis a question")
@app_commands.describe(question="Your question for Ignis")
async def ask(interaction: Interaction, question: str):
    await interaction.response.defer()
    response = await ask_openai(question)
    if len(response) > 2000:
        response = response[:1997] + "..."
    await interaction.followup.send(response)

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