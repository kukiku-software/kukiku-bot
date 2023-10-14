import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import json
import asyncio
import requests
import random
import time
import os

bot = commands.Bot(command_prefix='!', intents = discord.Intents.all())
update_task = None  # Declare update_task variable
weather_updates_enabled = False  # Control variable for weather updates

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

@bot.tree.command(name="test", description="command for testing the bot.")
async def test(interaction: discord.integrations):
    await interaction.response.send_message('Hello world.')

@bot.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.integrations):
    latency = round(bot.latency * 1000)

    await interaction.response.send_message(f'Pong! Bot latency is {latency}ms :satellite_orbital:.')

    # After the command execution, retrieve and update the configuration
    retrieve_and_update_config()

@bot.tree.command(name="countdown", description="Set a countdown in seconds.")
async def countdown(interaction: discord.interactions, seconds: int):
    if seconds <= 0:
        await interaction.response.send_message('Countdown duration must be greater than zero.', ephemeral=True)
        return

    end_time = datetime.utcnow() + timedelta(seconds=seconds)

    countdown_message = await interaction.response.send_message(content=f'Remaining Time: {seconds} seconds')

    while datetime.utcnow() < end_time:
        remaining_time = end_time - datetime.utcnow()
        remaining_seconds = int(remaining_time.total_seconds())

        countdown_message = await countdown_message.channel.fetch_message(countdown_message.id)  # Fetch the latest version of the message

        await countdown_message.edit(content=f'Remaining Time: {remaining_seconds} seconds')

        await asyncio.sleep(1)

    countdown_message = await countdown_message.channel.fetch_message(countdown_message.id)  # Fetch the latest version of the message
    await countdown_message.edit(content='Countdown has ended.')

    # After the command execution, retrieve and update the configuration
    retrieve_and_update_config()

@bot.tree.command(name="clear", description='Clear a specified number of messages.')
async def clear(interaction: discord.Interaction, amount: int):
    if amount <= 0:
        await interaction.response.send_message('Please specify a valid number of messages to clear.', ephemeral=True)
        return

    channel = interaction.channel
    deleted = await channel.purge(limit=amount + 1)

    await interaction.followup.send(f"Successfully deleted {len(deleted) - 1} messages.", ephemeral=True)

    # After the command execution, retrieve and update the configuration
    retrieve_and_update_config()

@bot.tree.command(name="serverinfo", description="Get server information")
async def serverinfo(interaction: discord.interactions):
    guild = interaction.guild

    server_name = guild.name
    total_members = guild.member_count
    creation_date = guild.created_at.strftime("%Y-%m-%d %H:%M:%S")

    await interaction.response.send_message(f"Server: {server_name}\nTotal members: {total_members}\nCreated at: {creation_date}", ephemeral=True)

    # After the command execution, retrieve and update the configuration
    retrieve_and_update_config()

@bot.tree.command(name="userinfo", description="Get user information")
async def userinfo(interaction: discord.interactions, member: discord.Member = None):
    if member is None:
        member = interaction.author

    # Retrieve user information
    username = member.name
    user_id = member.id
    joined_at = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")

    # Send the user information as a message
    await interaction.response.send_message(f"User: {username}\nID: {user_id}\nJoined at: {joined_at}", ephemeral=True)

    # After the command execution, retrieve and update the configuration
    retrieve_and_update_config()

@bot.tree.command(name="roll", description="Roll a random number")
async def roll(interaction: discord.interactions, number: int):
    # Generate a random number between 1 and the specified number
    rolled_number = random.randint(1, number)
    await interaction.response.send_message(f"You rolled: {rolled_number}")

    # After the command execution, retrieve and update the configuration
    retrieve_and_update_config()

@bot.tree.command(name="help", description="Show available commands")
async def help_command(interaction: discord.interactions):
    # Dictionary of commands and descriptions
    commands = {
        "help": "Show available commands",
        "ping": "Check the bot's latency",
        "userinfo <user>": "Get user information",
        "serverinfo": "Get the servers information",
        "clear <number>": "Clear a specified number of messages",
        "countdown <number>": "Start a countdown timer",
        "roll <number>": "Roll a random number",
        "weather <bool>": "start or stop the weather updates."
        # Add more commands and descriptions here
    }

    # Create an embed for the help message
    embed = discord.Embed(title="Bot Commands", description="Here are the available commands:")

    # Add command descriptions from the dictionary
    for command, description in commands.items():
        embed.add_field(name=command, value=description, inline=False)

    # Send the help message as a response
    await interaction.response.send_message(embed=embed, ephemeral=True)

    # After the command execution, retrieve and update the configuration
    retrieve_and_update_config()

@bot.tree.command(name="urban", description="Get a definition from Urban Dictionary")
async def urban_dictionary(interaction: discord.Interaction, term: str):
    # Make a request to the Urban Dictionary API
    url = f"https://api.urbandictionary.com/v0/define?term={term}"
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        # Check if there are any definitions for the term
        if data["list"]:
            # Get a random definition from the list
            definition = random.choice(data["list"])["definition"]
            
            # Send the definition to the user
            await interaction.response.send_message(f"**{term.capitalize()}**:\n{definition}")
        else:
            await interaction.response.send_message("No definitions found for that term.")
    else:
        # If there was an error, send an error message
        await interaction.response.send_message("Oops! Something went wrong while fetching the definition. Please try again later.")

    # After the command execution, retrieve and update the configuration
    retrieve_and_update_config()

@bot.tree.command(name="chucknorris", description="Get a Chuck Norris joke")
async def chuck_norris_joke(interaction: discord.Interaction):
    # Make a request to the Chuck Norris API
    url = "https://api.chucknorris.io/jokes/random"
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        joke = data["value"]
        
        # Send the joke to the user
        await interaction.response.send_message(joke)
    else:
        # If there was an error, send an error message
        await interaction.response.send_message("Oops! Something went wrong while fetching the joke. Please try again later.")

    # After the command execution, retrieve and update the configuration
    retrieve_and_update_config()

@bot.tree.command(name="wikipedia", description="Get a summary from Wikipedia")
async def wikipedia_summary(interaction: discord.Interaction, term: str):
    try:
        # Make a request to the Wikipedia API
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{term}"
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            summary = data.get("extract", "No summary found.")

            # Send the summary to the user
            await interaction.response.send_message(summary)
        else:
            # If there was an error, send an error message
            await interaction.response.send_message("Oops! Something went wrong while fetching the information. Please try again later.")
    except Exception:
        # If there was an unexpected error, send a general error message
        await interaction.response.send_message("Oops! Something went wrong while fetching the information. Please try again later.")

    # After the command execution, retrieve and update the configuration
    retrieve_and_update_config()

@bot.tree.command(name="convert", description="Convert currency using ExchangeRate-API")
async def currency_conversion(interaction: discord.Interaction, from_currency: str, to_currency: str, amount: float):
    try:
        # Make a request to the ExchangeRate-API for currency conversion
        url = f"https://v6.exchangerate-api.com/v6/{currency_key}/latest/{from_currency.upper()}"
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            print(currency_key)

            # Check if the currencies are valid
            if to_currency.upper() in data["conversion_rates"]:
                # Perform the currency conversion
                conversion_rate = data["conversion_rates"][to_currency.upper()]
                converted_amount = amount * conversion_rate

                # Send the result to the user
                await interaction.response.send_message(f"{amount} {from_currency.upper()} is equal to {converted_amount:.2f} {to_currency.upper()}")
            else:
                await interaction.response.send_message("Invalid target currency.")
        else:
            # If there was an error, send an error message
            await interaction.response.send_message("Oops! Something went wrong while performing the conversion. Please try again later.")
    except Exception:
        # If there was an unexpected error, send a general error message
        await interaction.response.send_message("Oops! Something went wrong while performing the conversion. Please try again later.")
        
    # After the command execution, retrieve and update the configuration
    retrieve_and_update_config()

def main():
    retrieve_and_update_config()
    bot.run(token)

if __name__ == '__main__':
    main()


# After the command execution, retrieve and update the configuration
retrieve_and_update_config() 
