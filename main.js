const { Client, Collection } = require('discord.js');
const client = new Client({ intents: ['GUILDS', 'GUILD_MESSAGES'] });

// Load all of the commands
const commands = new Collection();
const commandFiles = require.context('./commands', false, /\.js$/);
for (const file of commandFiles.keys()) {
  const command = require(`./commands${file}`);
  commands.set(command.name, command);
}

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
