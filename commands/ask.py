from discord import app_commands, Interaction
from utils.openai_api import ask_openai

# Global dictionary to store conversation history per user
conversation_history = {}

def setup(bot):
    @bot.tree.command(name="ask", description="Ask Ignis a question with context")
    @app_commands.describe(question="Your question for Ignis")
    async def ask(interaction: Interaction, question: str):
        user_id = interaction.user.id

        # Initialise history if first question
        if user_id not in conversation_history:
            conversation_history[user_id] = []

        # Append the new user message
        conversation_history[user_id].append({"role": "user", "content": question})

        # Store only the last 10 messages to manage token usage
        conversation_history[user_id] = conversation_history[user_id][-10:]

        # Call OpenAI with the last 10 messages
        response = await ask_openai(conversation_history[user_id])

        # Append assistant's reply to history
        conversation_history[user_id].append({"role": "assistant", "content": response})

        # Ensure Discord message length limit
        if len(response) > 2000:
            response = response[:1997] + "..."

        await interaction.response.send_message(response)