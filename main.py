import asyncio
import os
import sys
from typing import List

import discord
from aiohttp import ClientSession
from discord.ext import commands

from config import config
from database import DatabaseSessionManager


class OsuBot(commands.Bot):
    def __init__(self,
                 *args,
                 session: ClientSession,
                 init_extensions: List[str],
                 **kwargs, ):
        super().__init__(*args, **kwargs)
        self.session = session
        self.init_extensions = init_extensions
        self.sessionmanager = DatabaseSessionManager(config.osu_db_url.get_secret_value())

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def setup_hook(self) -> None:
        for extension in self.init_extensions:
            await self.load_extension(extension)


async def main():
    async with ClientSession() as session:
        exts = [f'cogs.{file[:-3]}' for file in os.listdir(os.path.join(os.getcwd(), 'cogs')) if
                file.endswith('_cog.py')]
        intents = discord.Intents.all()
        async with OsuBot(
                session=session,
                init_extensions=exts,
                intents=intents,
                command_prefix='$',
        ) as bot:
            await bot.start(config.discord_bot_token.get_secret_value())


if __name__ == '__main__':
    # TODO logger а то заебали принты
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print('Stopping')
