import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import pathlib
import importlib

# Load environment variables such as the bot token and guild ID (for development)
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", 0))

# Initialise the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Load commands from the commands folder
commands_path = pathlib.Path("./commands")
for file in commands_path.glob("*.py"):
    module_name = f"commands.{file.stem}"
    try:
        imported = importlib.import_module(module_name)
        if hasattr(imported, "setup"):
            imported.setup(bot)
            print(f"✅ Loaded {module_name}")
    except Exception as e:
        print(f"❌ Failed to load {module_name}: {e}")

# Toggle between development and production
DEVELOPMENT = True

# Sync commands on startup
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

# Start the bot
if __name__ == "__main__":
    bot.run(TOKEN)