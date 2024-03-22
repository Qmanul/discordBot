from __future__ import annotations

import traceback

import aiosu.models
import discord
from discord import app_commands
from discord.ext import commands

from config import config
from osu.api import ripple_api, akatsuki_api, gatari_api, direct_api
from osu.osu_helper import OsuHelper, OsuClient


class OsuCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self._bancho_client = aiosu.v2.Client(client_id=config.osu_client_id.get_secret_value(),
                                              client_secret=config.osu_client_secret.get_secret_value())
        self._ripple_client = ripple_api.RippleClient(token=config.ripple_token.get_secret_value())
        self._ripplerx_client = ripple_api.RippleRelaxClient(token=config.ripple_token.get_secret_value())
        self._akatsuki_client = akatsuki_api.AkatsukiClient()
        self._akatsukirx_client = akatsuki_api.AkatsukiRelaxClient()
        self._gatari_client = gatari_api.GatariClient()
        self._direct_client = direct_api.DirectClient()

        self.api_client_map = {
            'bancho': self._bancho_client,
            'ripple': self._ripple_client,
            'ripplerx': self._ripplerx_client,
            'akatsuki': self._akatsuki_client,
            'akatsukirx': self._akatsukirx_client,
            'gatari': self._gatari_client,
            'direct': self._direct_client,
        }

        self.osu_helper = OsuHelper(OsuClient(self.api_client_map))

    @commands.hybrid_command(name='link', aliases=['osuset'])
    async def osu_link(
            self,
            ctx: commands.Context[commands.Bot],
            username: str) -> None:
        """
        Link user to an osu profile
        Parameters
        ---------
        username: str
            player's username
        """
        async with self.bot.sessionmanager.session() as session:
            resp = await self.osu_helper.process_user_link(session, username=username, discord_id=ctx.author.id)

        await ctx.send(resp, ephemeral=True)

    @commands.hybrid_command(name='recent', aliases=['rs', ])
    async def osu_recent(
            self,
            ctx: commands.Context[commands.Bot],
            username: str | None = None,
            limit: app_commands.Range[int, 0, 5] = 1,
            server: str = 'bancho') -> None:
        """
        get user recent score
        Parameters
        ---------
        username: str
          player's username
        limit: app_commands.Range[int, 0, 5]
          number of scores to return
        server: str
          preferred server
        """
        async with self.bot.sessionmanager.session() as session:
            resp = await self.osu_helper.process_recent_scores(session, username=username, limit=limit,
                                                               discord_id=ctx.author.id, server=server)

        await self.return_embed_or_string(resp, ctx)

    @commands.hybrid_command(name='osu')
    async def osu_info(
            self, ctx: commands.Context[commands.Bot],
            username: str = None,
            gamemode: aiosu.models.Gamemode = aiosu.models.Gamemode.STANDARD,
            server: str = 'bancho', detailed: bool = False) -> None:
        """
        get user statistics
        Parameters
        ---------
        username: str
            player's username
        gamemode: str
            preferred gamemode
        detailed: bool
            detailed info
        server: str
            preferred server
        """
        await ctx.defer(ephemeral=True)
        async with self.bot.sessionmanager.session() as session:
            resp = await self.osu_helper.process_user_info(session, username=username, discord_id=ctx.author.id,
                                                           gamemode=gamemode, detailed=detailed, server=server)

            await self.return_embed_or_string(resp, ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('Something went wrong', ephemeral=True)
        print("".join(traceback.format_exception(type(error), error, error.__traceback__)))

    @osu_info.autocomplete('server')
    @osu_recent.autocomplete('server')
    async def server_autocomplete(
            self,
            interaction: discord.Interaction,
            current: str) -> list[app_commands.Choice[str]]:
        options = self.api_client_map.keys()
        return [app_commands.Choice(name=option, value=option) for option in options if
                option.lower().startswith(current.lower())][:25]

    @staticmethod
    async def return_embed_or_string(response: discord.Embed | str, ctx: commands.Context) -> None:
        if isinstance(response, discord.Embed):
            await ctx.send(embed=response, ephemeral=True)
        else:
            await ctx.send(response, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(OsuCog(bot))
