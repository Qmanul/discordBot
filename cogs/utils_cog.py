import traceback

import discord
from discord.ext import commands

from crud.tracking_crud import insert_guild, delete_guild


class UtilsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        async with self.bot.sessionmanager.session() as session:
            print(f'joined guild {guild.name}: {guild.id}')
            await insert_guild(session, guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        async with self.bot.sessionmanager.session() as session:
            print(f'left guild {guild.name}: {guild.id}')
            await delete_guild(session, guild.id)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('Something went wrong', ephemeral=True)
        print("".join(traceback.format_exception(type(error), error, error.__traceback__)))


async def setup(bot: commands.Bot):
    await bot.add_cog(UtilsCog(bot))
