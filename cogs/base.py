from __future__ import annotations

import traceback

import discord
from discord.ext import commands


class BaseCogGroup(commands.GroupCog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    @staticmethod
    async def return_embed_or_string(response: discord.Embed | str, interaction: discord.Interaction) -> None:
        if isinstance(response, discord.Embed):
            await interaction.followup.send(embed=response, ephemeral=True)
        else:
            await interaction.followup.send(content=response, ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction,
                                    error: discord.app_commands.AppCommandError):
        await interaction.followup.send('Something went wrong', ephemeral=True)
        print("".join(traceback.format_exception(type(error), error, error.__traceback__)))
