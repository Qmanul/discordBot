from __future__ import annotations

import struct

import discord
from aiordr import ordrClient
from aiordr.exceptions import APIException
from aiordr.models import RenderFinishEvent, RenderProgressEvent, RenderFailEvent
from aiosu.models import Gamemode
from orjson import orjson
from sqlalchemy.ext.asyncio import AsyncSession

from constants import RENDER_SKIN, RENDER_NAME
from crud import get_render, insert_render


class RenderHelper:
    def __init__(self, client: ordrClient) -> None:
        self.client = client
        self.queue: dict[int: RenderOngoing] = {}

        @self.client.on_render_fail
        async def render_fail(event: RenderFailEvent):
            if render := self.queue.pop(event.render_id, None):
                await render.failed(event)

        @self.client.on_render_finish
        async def render_finish(event: RenderFinishEvent):
            if render := self.queue.pop(event.render_id, None):
                await render.finished(event.video_url)

        @self.client.on_render_progress
        async def render_progress(event: RenderProgressEvent):
            if render := self.queue.get(event.render_id):
                await render.update_progress(event.progress)

        @self.client.socket.event
        async def connect():
            print(f'Websocket connected sid: {self.client.socket.get_sid()}')

        @self.client.socket.event
        async def disconnect():
            print(f'Websocket disconnected')

    async def process_render(self, session: AsyncSession, replay: discord.Attachment, inter: discord.Interaction):
        if not replay.filename.endswith('.osr'):
            return await inter.edit_original_response(content=f'Incorrect replay file')

        gamemode, score_id = OsrUnpacker(await replay.read()).parse()
        if not gamemode == Gamemode.STANDARD:
            return await inter.edit_original_response(content=f'Incorrect gamemode, o!rdr supports only std')

        if render := await get_render(session, score_id):
            return await inter.edit_original_response(
                content=f'<@{inter.user.id}> already rendered {render.render_url}')

        await inter.edit_original_response(content=f'Requesting render')

        try:
            resp = await self.client.create_render(
                username=RENDER_NAME,
                skin=RENDER_SKIN,
                replay_url=replay.url,
                custom_skin=True,
            )

            await inter.edit_original_response(content=resp.message)
            self.queue[resp.render_id] = RenderOngoing(inter, score_id, session)

        except (APIException, orjson.JSONDecodeError) as e:
            print(e)
            await inter.edit_original_response(content='Something went wrong')


class RenderOngoing:
    def __init__(
            self,
            interaction: discord.Interaction,
            score_id: int,
            session: AsyncSession,
    ):
        self.interaction = interaction
        self.score_id = score_id
        self.session = session

    async def update_progress(self, progress: str):
        await self.interaction.edit_original_response(content=progress)

    async def failed(self, event: RenderFailEvent):
        await self.interaction.edit_original_response(content=f'{event.error_message}, {event.error_code.name}')

    async def finished(self, url: str):
        await self.interaction.edit_original_response(content=f'<@{self.interaction.user.id}> render done {url}')
        await insert_render(self.session, self.score_id, url)


# я рот ебал весь парсер писать, так что только нужное
class OsrUnpacker:
    def __init__(self, replay_buffer):
        self.replay_buffer = replay_buffer
        self.offset = 0

    def unpack_byte(self):
        return self.unpack('b')

    def unpack_short(self):
        return self.unpack('h')

    def unpack_integer(self):
        return self.unpack('i')

    def unpack_long(self):
        return self.unpack('l')

    def unpack_bool(self):
        return self.unpack('?')

    def unpack_long_long(self):
        return self.unpack('q')

    def unpack_string(self):
        if self.replay_buffer[self.offset] == 0x00:
            self.offset += 1
            return

        if self.replay_buffer[self.offset] == 0x0b:
            self.offset += 1
            length = self.leb128_decode()
            # res = self.replay_buffer[self.offset: self.offset + length].decode('utf-8')
            self.offset += length
            return
            # return res

        raise ValueError

    # def unpack_life_bar_graph(self):
    #     life_bar: str = self.unpack_string()
    #     try:
    #         life_bar = life_bar.strip(',')
    #         return [LifeBarState(*state.split('|')) for state in life_bar.split(',')]
    #     except TypeError:
    #         return

    # def unpack_timestamp(self):
    #     ticks = self.unpack('q')
    #     time = datetime.min + timedelta(milliseconds=ticks / 10000)
    #     return time

    def unpack_replay_data(self):
        length = self.unpack_integer()
        self.offset += 1
        # data = self.replay_buffer[self.offset:self.offset + length]
        self.offset += length
        # data = lzma.decompress(data)

    def unpack(self, format: str):
        res = struct.unpack_from(f'<{format}', self.replay_buffer, self.offset)[0]
        self.offset += struct.calcsize(format)
        return res

    # https://en.wikipedia.org/wiki/LEB128
    def leb128_decode(self):
        result = 0
        shift = 0
        while True:
            byte = self.replay_buffer[self.offset]
            result = result | ((byte & 0b01111111) << shift)
            self.offset += 1
            if (byte & 0b10000000) == 0x00:
                break
            shift += 7
        return result

    def parse(self):
        mode = Gamemode(self.unpack_byte())
        self.unpack_integer()
        self.unpack_string()
        self.unpack_string()
        self.unpack_string()
        self.unpack_short()
        self.unpack_short()
        self.unpack_short()
        self.unpack_short()
        self.unpack_short()
        self.unpack_short()
        self.unpack_integer()
        self.unpack_short()
        self.unpack_bool()
        self.unpack_integer()
        self.unpack_string()
        self.unpack_long_long()
        self.unpack_replay_data()
        score_id = self.unpack_long()
        return mode, score_id

# @dataclasses.dataclass
# class LifeBarState:
#     time: int
#     value: float
#
#     def __post_init__(self):
#         self.time = int(self.time)
#         self.value = float(self.value)
#
#
# @dataclasses.dataclass
# class Replay:
#     gamemode: Gamemode
#     version: int
#     beatmap_hash: str
#     username: str
#     replay_hash: str
#     count_300: int
#     count_100: int
#     count_50: int
#     count_geki: int
#     count_katu: int
#     count_miss: int
#     score: int
#     combo: int
#     perfect: bool
#     mods: Mod
#     life_bar_graph: list[LifeBarState] | None
#     timestamp: datetime
#     replay_data: list
#     id: int
#     seed: int | None
