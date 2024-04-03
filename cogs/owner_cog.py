import traceback

from discord.ext import commands

from constants import MAIN_GUILD_ID


class OwnerCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_check(self, ctx: commands.Context[commands.Bot]) -> bool:
        check = str(ctx.guild.id) == MAIN_GUILD_ID and await self.bot.is_owner(ctx.author)
        return check

    @commands.command(aliases=['st', ])
    async def sync_tree(self, ctx: commands.Context[commands.Bot]) -> None:
        synced = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} commands globally")

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
