from discord import app_commands, Interaction

def setup(bot):
    @bot.tree.command(name="hello", description="Say hi to Ignis")
    async def hello(interaction: Interaction):
        await interaction.response.send_message("👋 Hey! I’m Ignis, your AI study buddy. I can answer questions, explain concepts and more! Try /help to see what I can do.")