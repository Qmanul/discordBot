import re

import discord.app_commands

from cogs import *
from crud import vasserman_crud


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


class VassermanCog(BaseCogGroup, name='vasserman'):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)

    @discord.app_commands.command(name='add')
    async def add_score(self, interaction: discord.Interaction, user: discord.User, amount: int = 1):
        await interaction.response.defer()
        if amount <= 0:
            return await interaction.edit_original_response(content=f'Ты еблан добавлять {amount}?')

        async with self.bot.sessionmanager.session() as session:
            await vasserman_crud.change_score(session, user_id=user.id, guild_id=interaction.guild.id, score=amount)
        await interaction.edit_original_response(content=f'Увеличил очки <@{user.id}> на {amount}')

    @discord.app_commands.command(name='decrease')
    async def decrease_score(self, interaction: discord.Interaction, user: discord.User, amount: int = 1):
        await interaction.response.defer()
        if amount <= 0:
            return await interaction.edit_original_response(content=f'Ты еблан уменьшать на {amount}?')

        try:
            async with self.bot.sessionmanager.session() as session:
                await vasserman_crud.change_score(session, user_id=user.id, guild_id=interaction.guild.id,
                                                  score=-amount)
        except ValueError:
            await interaction.edit_original_response(content=f'Ошибка очки не могут быть меньше нуля')
        else:
            await interaction.edit_original_response(content=f'Уменьшил очки <@{user.id}> на {amount}')

    @discord.app_commands.command(name='leaderboard')
    async def show_leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()

        async with self.bot.sessionmanager.session() as session:
            users = await vasserman_crud.get_users(session, guild_id=interaction.guild.id)

        embed = discord.Embed(title=f"Таблица лидеров {interaction.guild.name}", description='')

        if not users:
            embed.description = 'Пуста!'
            return await interaction.edit_original_response(embed=embed)

        for user in sorted(users, reverse=True, key=lambda x: x.score):
            if not interaction.guild.get_member(user.user_id):
                await vasserman_crud.delete_user(session, user)
                continue
            embed.description += f"<@{user.user_id}>: {user.score}\n"

        await interaction.edit_original_response(embed=embed)

    @discord.app_commands.command(name='user')
    async def show_user(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()
        if not user:
            user = interaction.user

        async with self.bot.sessionmanager.session() as session:
            if not (db_user := await vasserman_crud.get_user(session, user_id=user.id, guild_id=interaction.guild.id)):
                db_user = await vasserman_crud.insert_user(session, user_id=user.id, guild_id=interaction.guild.id)

        await interaction.edit_original_response(content=f'У <@{db_user.user_id}> {db_user.score} очка')


async def setup(bot: commands.Bot):
    await bot.add_cog(FunCog(bot))
    await bot.add_cog(VassermanCog(bot))
