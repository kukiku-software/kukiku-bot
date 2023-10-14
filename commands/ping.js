const { SlashCommandBuilder } = require('discord.js');

const pingCommand = new SlashCommandBuilder()
  .setName('ping')
  .setDescription('Sends a pong response.');

module.exports = async interaction => {
  await interaction.reply('Pong!');
};
