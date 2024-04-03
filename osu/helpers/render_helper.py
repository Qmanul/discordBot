import discord
from aiordr import ordrClient
from aiordr.exceptions import APIException
from aiordr.models import RenderFinishEvent, RenderProgressEvent, RenderFailEvent

RENDER_NAME = 'Qmanul'
RENDER_SKIN = 17866


class RenderHelper:
    def __init__(self, client: ordrClient) -> None:
        self.client = client
        self.queue: dict[int: RenderOngoing] = {}

        @self.client.on_render_fail
        async def render_fail(event: RenderFailEvent):
            try:
                render: RenderOngoing = self.queue.pop(event.render_id)
                await render.update_progress(f'failed, {event.error_message}')
            except KeyError:
                pass

        @self.client.on_render_finish
        async def render_finish(event: RenderFinishEvent):
            try:
                render: RenderOngoing = self.queue.pop(event.render_id)
                await render.update_progress(event.video_url)
            except KeyError:
                pass

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

    async def process_render(self, replay: discord.Attachment, inter: discord.Interaction):
        if not replay.filename.endswith('.osr'):
            return await inter.edit_original_response(content=f'Incorrect replay file')

        await inter.edit_original_response(content=f'Requesting render')

        try:
            resp = await self.client.create_render(
                username=RENDER_NAME,
                skin=RENDER_SKIN,
                replay_url=replay.url,
                custom_skin=True,
            )
            await inter.edit_original_response(content=resp.message)
            self.queue[resp.render_id] = RenderOngoing(inter)

        except APIException:
            await inter.edit_original_response(content='Something went wrong')


class RenderOngoing:
    def __init__(
            self,
            interaction: discord.Interaction,
    ):
        self.interaction = interaction

    async def update_progress(self, progress: str):
        await self.interaction.edit_original_response(content=progress)

    async def failed(self):
        ...

    async def completed(self):
        ...
