import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.openai_api import ask_openai
import redis
import json

load_dotenv() # load environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", 0))
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# redis client setup
try:
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        ssl=True,
        decode_responses=True
    )
    if r.ping():
        print("Connected to Redis")
except redis.ConnectionError:
    print("Failed to connect to Redis")
    exit()

# dev toggle (true when testing commands in a specific guild or false when deploying globally)
DEVELOPMENT = False
guild = discord.Object(id=GUILD_ID) if DEVELOPMENT else None

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
        "**/ask** [question] - Ask Ignis a question and get a detailed response. Stores context of the last 5 responses and removes the earliest response if the limit is reached.\n"
        "**/reset** - Reset your conversation history with Ignis.\n"
        "**/define** [term] - Get a simple definition for a term or phrase.\n"
        "**/explainlikeim5** [concept] - Breaks down a complex concept into simple terms.\n"
        "**/summarise** [text] - Transform a long piece of text into a concise summary.\n"
        "**/translate** [text] [language] - Translate text into a specified language.\n"
        "**/quiz** [topic] [num_questions] - Generate a short quiz on a specified topic with up to 10 questions.\n"
    )
    await interaction.response.send_message(help_text)

# /ask (uses redis to store conversation history)
@bot.tree.command(
        name="ask",
        description="Ask Ignis a question",
        guild=guild
        )
async def ask(interaction: discord.Interaction, question: str):
    user_id = interaction.user.id
    
    redis_key = f"conversation_history:{user_id}"
    user_message = {"role": "user", "content": question}
    r.rpush(redis_key, json.dumps(user_message))
    r.ltrim(redis_key, -10, -1)
    await interaction.response.defer()
    history_json = r.lrange(redis_key, 0, -1)
    messages = [json.loads(message) for message in history_json]
    response = await ask_openai(messages)
    assistant_message = {"role": "assistant", "content": response}
    r.rpush(redis_key, json.dumps(assistant_message))
    r.ltrim(redis_key, -10, -1)

    if len(response) > 2000:
        response = response[:1900] + "... \n\n*Response truncated due to length.*"
    
    reply = f"{interaction.user.mention} asked Ignis: {question}\n\n{response}"
    await interaction.followup.send(reply)

# /reset
@bot.tree.command(
        name="reset",
        description="Reset conversation context",
        guild=guild
        )
async def reset(interaction: discord.Interaction):
    redis_key = f"conversation_history:{interaction.user.id}"
    r.delete(redis_key)
    await interaction.response.send_message("Your conversation history has been reset ✅")

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
        response = response[:1900] + "... \n\n*Response truncated due to length.*"
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
    reply = f"{interaction.user.mention} used /explainlikeim5 to explain: {concept}\n\n{response}"
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
        response = response[:1900] + "... \n\n*Response truncated due to length.*"
    reply = f"{interaction.user.mention} here is a summary on your topic:\n\n{response}"
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
        response = response[:1900] + "... \n\n*Response truncated due to length.*"
    reply = f"{interaction.user.mention} here is your text translated to {language}:\n\n{response}"
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
                "1. Provide the number of questions requested, but never more than 10. If the user requests more than 10, state that 10 is the maximum and prompt the user to try running /quiz again.\n"
                "2. Each question should be numbered and bolded.\n"
                "3. Each answer should appear immediately below its question, "
                "not numbered or bolded, and wrapped in double pipes ||like this|| to spoiler it for Discord.\n"
                "4. Format the response clearly so that each question and answer is on its own line."
                "5. If an invalid quiz topic is provided, respond with a message indicating that the topic is invalid and prompt the user to try running /quiz again."
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
        response = response[:1900] + "... \n\n*Response truncated due to length.*"
    reply = f"{interaction.user.mention} here is a {num_questions} quiz on {topic}:\n\n{response}"
    await interaction.followup.send(reply)

# startup actions
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # configure discord presence
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

# start the bot
async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())