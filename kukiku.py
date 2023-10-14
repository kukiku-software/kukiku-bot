import discord

bot = discord.Client()

# Load the command extension
bot.load_extension('commands.test')

if __name__ == '__main__':
    bot.run('YOUR_BOT_TOKEN')
