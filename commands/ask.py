from discord import app_commands, Interaction
from utils.openai_api import ask_openai

def setup(bot):
    @bot.tree.command(name="ask", description="Ask Ignis a question")
    @app_commands.describe(question="Your question for Ignis")
    async def ask(interaction: Interaction, question: str):
        await interaction.response.defer()
        response = await ask_openai(question)
        if len(response) > 2000:
            response = response[:1997] + "..."
        await interaction.followup.send(response)