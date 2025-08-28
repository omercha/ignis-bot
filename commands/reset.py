from discord import app_commands, Interaction
from commands.ask import conversation_history

def setup(bot):
    @bot.tree.command(name="reset", description="Reset your conversation history with Ignis")
    async def reset(interaction: Interaction):
        user_id = interaction.user.id
        if user_id in conversation_history:
            conversation_history[user_id] = []
            await interaction.response.send_message("✅ Your conversation history has been reset.")
        else:
            await interaction.response.send_message("ℹ️ You have no conversation history to reset.")