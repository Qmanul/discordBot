from cogs import *

from constants import MAIN_GUILD_ID, OWNER_ID
from crud.tracking_crud import insert_guild, delete_guild


class OwnerCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_check(self, ctx: commands.Context[commands.Bot]) -> bool:
        check = ctx.guild.id == MAIN_GUILD_ID and ctx.author.id == OWNER_ID
        return check

    # сука ёбанный хуй апи дискорда уже ведёт учет сервов где есть бот
    # блять я опять написал код который нахуй не нужон
    # пизда надо же будет теперь ебаться с апи
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

    @commands.command(aliases=['st', ])
    async def sync_tree(self, ctx: commands.Context[commands.Bot]) -> None:
        synced = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} commands globally")

    @commands.command(name='dummy')
    async def dummy(self, ctx: commands.Context[commands.Bot]) -> None:
        async for guild in self.bot.fetch_guilds(with_counts=False):
            print(guild.id)
        await ctx.send('Success')

    @commands.command(name='shutdown', aliases=['stop'])
    async def shutdown(self, ctx: commands.Context[commands.Bot]) -> None:
        """
        bye bye
        """
        await ctx.send('Stopping')
        await self.bot.close()

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('Something went wrong', ephemeral=True)
        print("".join(traceback.format_exception(type(error), error, error.__traceback__)))


async def setup(bot: commands.Bot):
    await bot.add_cog(OwnerCog(bot))
