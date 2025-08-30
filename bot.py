import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.openai_api import ask_openai

# -------------------- SETUP --------------------

# load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", 0))

# bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# dev toggle (true when testing commands in a specific guild, false to deploy globally)
DEVELOPMENT = True
guild = discord.Object(id=GUILD_ID) if DEVELOPMENT else None

# global variable used to store conversation history (context)
conversation_history = {}

# -------------------- COMMANDS --------------------

# # /test (ensure development is set to True)
# @bot.tree.command(
#         name="test",
#         description="Test command to check if commands are synced properly"
# )
# async def test(interaction: discord.Interaction):
#     await interaction.response.send_message("Commands have synced properly")

# /help
@bot.tree.command(
        name="help",
        description="Get a list of available commands and their functions"
        )
async def help(interaction: discord.Interaction):
    help_text = (
        "List of currently available commands:\n"
        "**/ask** [question] - *Ask Ignis a question and get a detailed response.*\n"
        "**/reset** - *Reset your conversation history with Ignis.*\n"
        "**/define** [term] - *Get a simple definition for a term or phrase.*\n"
    )
    await interaction.response.send_message(help_text)

# # /hello
# @bot.tree.command(
#         name="hello",
#         description="Say hi to Ignis"
#         )
# async def hello(interaction: discord.Interaction):
#     await interaction.response.send_message(f"👋 Hey! I’m Ignis, your AI study buddy. I can answer questions, explain concepts and more! Try /help to see what I can do.")

# /ask
@bot.tree.command(
        name="ask",
        description="Ask Ignis a question and get a detailed response"
        )
async def ask(interaction: discord.Interaction, question: str):
    user_id = interaction.user.id
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({"role": "user", "content": question})
    conversation_history[user_id] = conversation_history[user_id][-10:]
    await interaction.response.defer()
    response = await ask_openai(conversation_history[user_id])
    conversation_history[user_id].append({"role": "assistant", "content": response})
    if len(response) > 2000:
        response = response[:1997] + "..."
    await interaction.followup.send(response)

# /reset
@bot.tree.command(
        name="reset",
        description="Reset your conversation with Ignis"
        )
async def reset(interaction: discord.Interaction):
    conversation_history[interaction.user.id] = []
    await interaction.response.send_message("✅ Your conversation has been reset.")

# /define
@bot.tree.command(
        name="define",
        description="Get a simple definition for a term or phrase"
        )
async def define(interaction: discord.Interaction, term: str):
    await interaction.response.defer()
    messages = [
        {"role": "system", "content": "You are a helpful study assistant that provides short, simple definitions."},
        {"role": "user", "content": f"Define: {term}"}
    ]
    response = await ask_openai(messages)
    await interaction.followup.send(response)

# -------------------- STARTUP --------------------

# necessary on_ready event
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if DEVELOPMENT:
        synced = await bot.tree.sync(guild=guild)
        print(f"Commands synced to guild {GUILD_ID}: {[cmd.name for cmd in synced]}")
    else:
        synced = await bot.tree.sync()
        print(f"Global commands synced: {[cmd.name for cmd in synced]}")

# main function to run the bot
async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())