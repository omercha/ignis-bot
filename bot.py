import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.openai_api import ask_openai

# load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", 0))

# bot initialisation
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# dev toggle (true when testing commands in a specific guild, false to deploy globally)
DEVELOPMENT = False
guild = discord.Object(id=GUILD_ID) if DEVELOPMENT else None

# global variable used to store context
conversation_history = {}


# --- COMMANDS ---
# /help
@bot.tree.command(
        name="help",
        description="List available commands",
        guild=guild
        )
async def help(interaction: discord.Interaction):
    help_text = (
        "__List of currently available commands:__\n\n"
        "**/help** - Display this message.\n"
        "**/ask** [question] - Ask Ignis a question and get a detailed response. Can store context for up to 10 responses.\n"
        "**/reset** - Reset your conversation's context with Ignis.\n"
        "**/define** [term] - Get a simple definition for a term or phrase.\n"
        "**/explainlikeim5** [concept] - Breaks down a complex concept into simple terms.\n"
        "**/summarise** [text] - Transform a long piece of text into a concise summary.\n"
        "**/translate** [text] [language] - Translate text into a specified language.\n"
        "**/quiz** [topic] [num_questions] - Generate a short quiz on a specified topic with up to 10 questions.\n"
    )
    await interaction.response.send_message(help_text)

# /ask
@bot.tree.command(
        name="ask",
        description="Ask Ignis a question",
        guild=guild
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
    
    reply = f"{interaction.user.mention} asked Ignis: {question}\n\n{response}"
    await interaction.followup.send(reply)

# /reset
@bot.tree.command(
        name="reset",
        description="Reset conversation context",
        guild=guild
        )
async def reset(interaction: discord.Interaction):
    conversation_history[interaction.user.id] = []
    await interaction.response.send_message("Your conversation has been reset ✅")

# /define
@bot.tree.command(
        name="define",
        description="Define a term or phrase",
        guild=guild
        )
async def define(interaction: discord.Interaction, term: str):
    await interaction.response.defer()
    messages = [
        {
            "role": "system", "content":
            "You are a helpful study assistant that provides short, simple definitions."
        },
        {
            "role": "user",
            "content": f"Define: {term}"
        }
    ]
    response = await ask_openai(messages)
    if len(response) > 2000:
        response = response[:1997] + "..."
    reply = f"{interaction.user.mention} requested a definition for: {term}\n\n{response}"
    await interaction.followup.send(reply)

# /explainlikeim5
@bot.tree.command(
        name="explainlikeim5",
        description="Explain a complex concept in simple terms",
        guild=guild
        )
async def explainlikeim5(interaction: discord.Interaction, concept: str):
    await interaction.response.defer()
    messages = [
        {
            "role": "system", 
            "content": "You are a helpful study assistant that explains complex concepts in simple terms."
        },
        {
            "role": "user",
            "content": f"Explain like I'm 5 years old: {concept}"
        }
    ]
    response = await ask_openai(messages)
    if len(response) > 2000:
        response = response[:1997] + "..."
    reply = f"{interaction.user.mention} asked Ignis to explain: {concept}\n\n{response}"
    await interaction.followup.send(reply)

# /summarise
@bot.tree.command(
        name="summarise",
        description="Summarise a long piece of text",
        guild=guild
)
async def summarise(interaction: discord.Interaction, text: str):
    await interaction.response.defer()
    messages = [
        {
            "role": "system",
            "content": "You are a helpful study assistant that converts long pieces of text into concise summaries."
        },
        {
            "role": "user",
            "content": f"Summarise the following text: {text}"
        }
    ]
    response = await ask_openai(messages)
    if len(response) > 2000:
        response = response[:1997] + "..."
    reply = f"{interaction.user.mention} asked Ignis to summarise:\n{text}\n\n{response}"
    await interaction.followup.send(reply)

# /translate
@bot.tree.command(
        name="translate",
        description="Translate text into a specified language",
        guild=guild
)
async def translate(interaction: discord.Interaction, text: str, language: str):
    await interaction.response.defer()
    messages = [
        {
            "role": "system",
            "content": "You are a helpful study assistant that translates text into a different language."
        },
        {
            "role": "user",
            "content": f"Translate the following text into {language}: {text}"
        }
    ]
    response = await ask_openai(messages)
    if len(response) > 2000:
        response = response[:1997] + "..."
    reply = f"{interaction.user.mention} asked Ignis to translate to {language}:\n{text}\n\n{response}"
    await interaction.followup.send(reply)

# /quiz
@bot.tree.command(
    name="quiz",
    description="Generate a short quiz on a specified topic",
    guild=guild
)
async def quiz(interaction: discord.Interaction, topic: str, num_questions: int):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful study assistant. "
                "When generating quiz questions, follow these rules:\n"
                "1. Provide the number of questions requested, but never more than 10. If the user requests more than 10, return 10 questions and clearly state at the start that 10 is the maximum.\n"
                "2. Each question should be numbered and bolded.\n"
                "3. Each answer should appear immediately below its question, "
                "not numbered, and wrapped in double pipes ||like this|| to spoiler it for Discord.\n"
                "4. Do not bold the answers.\n"
                "5. Format the response clearly so that each question and answer is on its own line."
            )
        },
        {
            "role": "user",
            "content": f"Please provide {num_questions} quiz questions on the topic: {topic}"
        }
    ]
    await interaction.response.defer()
    response = await ask_openai(messages)
    if len(response) > 2000:
        response = response[:1997] + "..."
    reply = f"{interaction.user.mention} requested a {num_questions}-question quiz on {topic}:\n\n{response}"
    await interaction.followup.send(reply)
# ----------------

# startup event
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # configure bot presence
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="Type /help for usage!")
    )
    
    # synchronise commands (either to a specific guild or globally)
    if DEVELOPMENT:
        synced = await bot.tree.sync(guild=guild)
        print(f"Commands synced to guild {GUILD_ID}: {[cmd.name for cmd in synced]}")
    else:
        synced = await bot.tree.sync()
        print(f"Global commands synced: {[cmd.name for cmd in synced]}")

async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())