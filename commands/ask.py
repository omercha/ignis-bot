from discord import app_commands, Interaction
from utils.openai_api import ask_openai

conversation_history = {}

async def setup(bot):
    @bot.tree.command(name="ask", description="Ask Ignis a question")
    @app_commands.describe(question="Your question for Ignis")
    async def ask(interaction: Interaction, question: str):
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