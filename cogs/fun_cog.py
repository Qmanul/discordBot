import re
import traceback

import discord
from discord import app_commands
from discord.ext import commands


class FunCog(commands.GroupCog, name='fun'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.emoji_url = 'https://cdn.discordapp.com/emojis/{id}.{extension}'
        self.emoji_pattern = re.compile(r'<a?:[a-zA-Z]+:[0-9]+>')

    @app_commands.command(name='add_emoji')
    async def add_emoji(self, interaction: discord.Interaction, emoji: str, custom_name: str = ''):
        await interaction.response.defer()
        if not re.fullmatch(self.emoji_pattern, emoji):
            return await interaction.edit_original_response(content='Incorrect emoji')

        animated, name, id = emoji.strip('<>').split(':')
        name = custom_name if custom_name else name
        extension = 'webp' if animated else 'gif'
        async with self.bot.session.get(self.emoji_url.format(id=id, extension=extension)) as resp:
            emoji = await interaction.guild.create_custom_emoji(name=name, image=await resp.read())

        await interaction.edit_original_response(content=f"Added emoji: {emoji}")

    async def cog_app_command_error(self, interaction: discord.Interaction,
                                    error: app_commands.AppCommandError):
        await interaction.followup.send('Something went wrong', ephemeral=True)
        print("".join(traceback.format_exception(type(error), error, error.__traceback__)))


async def setup(bot: commands.Bot):
    await bot.add_cog(FunCog(bot))
