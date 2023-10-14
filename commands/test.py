import discord

@bot.tree.command(name="test", description="command for testing the bot.")
async def test(interaction: discord.integrations):
    await interaction.response.send_message('Hello world.')
