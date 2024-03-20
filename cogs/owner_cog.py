from discord.ext import commands
from config import config


class OwnerCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_check(self, ctx: commands.Context[commands.Bot]) -> bool:
        check = str(ctx.guild.id) == config.testing_guild_id.get_secret_value() and await self.bot.is_owner(ctx.author)
        return check

    @commands.command()
    async def sync_tree(self, ctx: commands.Context[commands.Bot]) -> None:
        synced = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} commands globally")


async def setup(bot: commands.Bot):
    await bot.add_cog(OwnerCog(bot))
