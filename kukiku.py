import os
import discord

bot = discord.Client()

token = os.getenv('BOT_TOKEN')

# Load the command extension
bot.load_extension('commands.test')

if __name__ == '__main__':
    bot.run(token)
