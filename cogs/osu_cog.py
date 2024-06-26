from __future__ import annotations

import traceback

import discord
from aiosu.models import Gamemode
from aiosu.v2 import Client
from discord import app_commands
from discord.ext import commands, tasks

from config import config
from osu.api import (RippleClient, RippleRelaxClient, DirectClient, AkatsukiClient, GatariClient, AkatsukiRelaxClient,
                     OsutrackClient)
from osu.osu_helper import OsuHelper, OsuClient


class BaseCogGroup(commands.GroupCog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

        self._bancho_client = Client(client_id=config.osu_client_id.get_secret_value(),
                                     client_secret=config.osu_client_secret.get_secret_value())
        self._ripple_client = RippleClient(token=config.ripple_token.get_secret_value())
        self._ripplerx_client = RippleRelaxClient(token=config.ripple_token.get_secret_value())
        self._akatsuki_client = AkatsukiClient()
        self._akatsukirx_client = AkatsukiRelaxClient()
        self._gatari_client = GatariClient()
        self._direct_client = DirectClient()
        self._osutrack_client = OsutrackClient()

        self.api_client_map = {
            'bancho': self._bancho_client,
            'ripple': self._ripple_client,
            'ripplerx': self._ripplerx_client,
            'akatsuki': self._akatsuki_client,
            'akatsukirx': self._akatsukirx_client,
            'gatari': self._gatari_client,
            'direct': self._direct_client,
            'osutrack': self._osutrack_client,
        }

        self.osu_helper = OsuHelper(OsuClient(self.api_client_map))

    @staticmethod
    async def return_embed_or_string(response: discord.Embed | str, interaction: discord.Interaction) -> None:
        if isinstance(response, discord.Embed):
            await interaction.followup.send(embed=response, ephemeral=True)
        else:
            await interaction.followup.send(content=response, ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction,
                                    error: app_commands.AppCommandError):
        await interaction.followup.send('Something went wrong', ephemeral=True)
        print("".join(traceback.format_exception(type(error), error, error.__traceback__)))


# noinspection PyUnresolvedReferences
class OsuGroup(BaseCogGroup, name='osu'):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)

    #  ---------------- user info related ----------------
    @app_commands.command(name='link')
    async def ink(
            self,
            interaction: discord.Interaction,
            username: str) -> None:
        """
        Link user to an osu profile
        Parameters
        ---------
        username: str
            player's username
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.sessionmanager.session() as session:
            resp = await self.osu_helper.process_user_link(session, username=username, discord_id=interaction.user.id)

        await interaction.followup.send(content=resp, ephemeral=True)

    @app_commands.command(name='recent')
    async def recent(
            self,
            interaction: discord.Interaction,
            username: str = None,
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
        await interaction.response.defer(ephemeral=True)
        async with self.bot.sessionmanager.session() as session:
            resp = await self.osu_helper.process_recent_scores(session, username=username, limit=limit,
                                                               discord_id=interaction.user.id, server=server)

        await self.return_embed_or_string(resp, interaction)

    @commands.hybrid_command(name='osu')
    async def info(
            self,
            interaction: discord.Interaction,
            username: str = None,
            gamemode: Gamemode = Gamemode.STANDARD,
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
        await interaction.response.defer(ephemeral=True)
        async with self.bot.sessionmanager.session() as session:
            resp = await self.osu_helper.process_user_info(session, username=username, discord_id=interaction.user.id,
                                                           gamemode=gamemode, detailed=detailed, server=server)

            await self.return_embed_or_string(resp, interaction)

    @info.autocomplete('server')
    @recent.autocomplete('server')
    async def server_autocomplete(
            self,
            interaction: discord.Interaction,
            current: str) -> list[app_commands.Choice[str]]:
        options = self.api_client_map.keys()
        return [app_commands.Choice(name=option, value=option) for option in options if
                option.lower().startswith(current.lower())][:25]


# noinspection PyUnresolvedReferences
class TrackingGroup(BaseCogGroup, name='tracking'):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)
        self.poll_tracked_users.start()

    @app_commands.command(name='enable')
    async def enable_tracking(self, interaction: discord.Interaction):
        """
        placeholder
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.sessionmanager.session() as session:
            resp = await self.osu_helper.process_tracking_enable(session, channel=interaction.channel)

        await interaction.followup.send(content=resp, ephemeral=True)

    @app_commands.command(name='disable')
    async def disable_tracking(self, interaction: discord.Interaction):
        """
        placeholder
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.sessionmanager.session() as session:
            resp = await self.osu_helper.process_tracking_disable(session, channel=interaction.channel)

        await interaction.followup.send(content=resp, ephemeral=True)

    @app_commands.command(name='register')
    async def register_user(
            self,
            interaction: discord.Interaction,
            user: discord.User = None
    ) -> None:
        """
        placeholder
        """
        await interaction.response.defer(ephemeral=True)
        if not user:
            user = interaction.user
        async with self.bot.sessionmanager.session() as session:
            resp = await self.osu_helper.process_tracking_register(session, discord_id=user.id,
                                                                   channel=interaction.channel, )

        await interaction.followup.send(content=resp, ephemeral=True)

    @app_commands.command(name='link')
    async def link_user(
            self,
            interaction: discord.Interaction,
            username: str = None,
            gamemode: Gamemode = Gamemode.STANDARD,
    ) -> None:
        """
        placeholder
        """
        await interaction.response.defer(ephemeral=True)
        async with self.bot.sessionmanager.session() as session:
            resp = await self.osu_helper.process_tracking_link(session, discord_id=interaction.user.id,
                                                               username=username, gamemode=gamemode)

        await interaction.followup.send(content=resp, ephemeral=True)

    @tasks.loop(minutes=1)
    async def poll_tracked_users(self):
        async with self.bot.sessionmanager.session() as session:
            async for item in self.osu_helper.process_tracked_users(session):
                for channel_id in item[0]:
                    await self.bot.get_channel(channel_id).send(embed=item[1])

    @poll_tracked_users.error
    async def error_handler(self, error: Exception):
        print("".join(traceback.format_exception(type(error), error, error.__traceback__)))


async def setup(bot: commands.Bot):
    await bot.add_cog(OsuGroup(bot))
    await bot.add_cog(TrackingGroup(bot))
