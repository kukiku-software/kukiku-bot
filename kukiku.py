import os
import discord

bot = discord.Client()

def retrieve_and_update_config():
    global prefix, api_key, token, currency_key

    # Retrieve the configuration values from Heroku
    prefix = os.getenv('PREFIX')
    api_key = os.getenv('API_KEY')
    token = os.getenv('BOT_TOKEN')
    currency_key = os.getenv('CURRENCY_KEY')

    # Check if all configuration values are set
    if not prefix or not api_key or not token or not currency_key:
        raise Exception('Missing configuration values')

@bot.event
async def on_ready():
    print("Bot is up and ready!")
    try:
        synced = await bot.tree.sync()
        print("Synced commands")
    except Exception as e:
        print(e)

# Load the command extension
bot.load_extension('commands.test')

def main():
    retrieve_and_update_config()
    bot.run(token)

if __name__ == '__main__':
    main()
