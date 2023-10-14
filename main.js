const { Client, Collection } = require('discord.js');
const client = new Client({ intents: ['GUILDS', 'GUILD_MESSAGES'] });

// Load all of the commands
const commands = new Collection();
commands.set('ping', async interaction => {
  await interaction.reply('Pong!');
});

// Handle interaction events
client.on('interactionCreate', async interaction => {
  const command = commands.get(interaction.commandName);
  if (!command) return;

  try {
    await command(interaction);
  } catch (error) {
    console.error(error);
    await interaction.reply('Something went wrong!');
  }
});

// Login the bot
const token = process.env.token;
client.login(token);
