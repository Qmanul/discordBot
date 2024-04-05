import re

import discord.app_commands

from cogs import *


class FunCog(BaseCogGroup, name='fun'):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)
        self.emoji_url = 'https://cdn.discordapp.com/emojis/{id}.{extension}'
        self.emoji_pattern = re.compile(r'<a?:[a-zA-Z]+:[0-9]+>')

    @discord.app_commands.command(name='add_emoji')
    async def add_emoji(self, interaction: discord.Interaction, emoji: str, custom_name: str = ''):
        await interaction.response.defer()
        if not re.fullmatch(self.emoji_pattern, emoji):
            return await interaction.edit_original_response(content='Incorrect emoji')

        animated, name, id = emoji.strip('<>').split(':')
        name = custom_name if custom_name else name
        extension = 'gif' if animated else 'webp'
        async with self.bot.session.get(self.emoji_url.format(id=id, extension=extension)) as resp:
            emoji = await interaction.guild.create_custom_emoji(name=name, image=await resp.read())

        await interaction.edit_original_response(content=f"Added emoji: {emoji}")

    @discord.app_commands.command(name='get_avatar')
    async def ger_avatar(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()
        if not user:
            user = interaction.user

        return await interaction.edit_original_response(
            embed=discord.Embed(title=f'{user.name} avatar').set_image(url=user.display_avatar.url))


class VasermanCog(BaseCogGroup, name='vaserman'):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)

    @discord.app_commands.command(name='add')
    async def ger_avatar(self, interaction: discord.Interaction, user: discord.User, amount: int = 1):
        await interaction.response.defer()
        if amount <= 0:
            return await interaction.edit_original_response(content=f'Ты еблан добавлять {amount}?')

        async with self.bot.sessionmanager.session() as session:
            ...


async def setup(bot: commands.Bot):
    await bot.add_cog(FunCog(bot))
