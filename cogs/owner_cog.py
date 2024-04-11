from cogs import *

from constants import MAIN_GUILD_IDS, OWNER_ID
from crud import tracking_crud


class OwnerCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_check(self, ctx: commands.Context[commands.Bot]) -> bool:
        check = ctx.guild.id in MAIN_GUILD_IDS and ctx.author.id == OWNER_ID
        return check

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        print(f'joined guild {guild.name}: {guild.id}')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        async with self.bot.sessionmanager.session() as session:
            print(f'left guild {guild.name}: {guild.id}')
            await tracking_crud.delete_channel_by_guild_id(session, guild.id)

    @commands.command(aliases=['st'])
    async def sync_tree(self, ctx: commands.Context[commands.Bot]) -> None:
        synced = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} commands globally")

    @commands.command()
    async def leave(self, ctx: commands.Context[commands.Bot]) -> None:
        await ctx.send(f"Leaving guild {ctx.guild.name}")
        await ctx.guild.leave()

    @commands.command(name='dummy')
    async def dummy(self, ctx: commands.Context[commands.Bot]) -> None:
        print(ctx.author.id in ctx.guild.members)

        await ctx.send('Success')

    @commands.command(name='shutdown', aliases=['stop'])
    async def shutdown(self, ctx: commands.Context[commands.Bot]) -> None:
        await ctx.send('Stopping')
        await self.bot.close()

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('Something went wrong', ephemeral=True)
        print("".join(traceback.format_exception(type(error), error, error.__traceback__)))


async def setup(bot: commands.Bot):
    await bot.add_cog(OwnerCog(bot))
