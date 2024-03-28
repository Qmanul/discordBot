import asyncio

from socketio import AsyncClient

from osu.api.base_api import BaseClient


class OrdrSocketClient:
    def __init__(self, *args, **kwargs):
        self.client_args = args
        self.client_kwargs = kwargs
        self.client = None
        self.namespace = '/'
        self.connected_event = asyncio.Event()
        self.connected = False
        self.input_event = asyncio.Event()
        self.input_buffer = []
        self.on_event_callback = None

    async def connect(self, url, headers=None, auth=None, transports=None,
                      namespace='/', socketio_path='socket.io',
                      wait_timeout=5, on_event_callback=print):
        if headers is None:
            headers = {}
        if self.connected:
            raise RuntimeError('Already connected')
        self.namespace = namespace
        self.input_buffer = []
        self.input_event.clear()
        self.on_event_callback = on_event_callback
        self.client = AsyncClient(*self.client_args, **self.client_kwargs)

        @self.client.event(namespace=self.namespace)
        async def connect():
            print(f'Connection established sid: {self.sid}')
            self.connected = True
            self.connected_event.set()

        @self.client.event(namespace=self.namespace)
        async def disconnect():
            print('Disconnected from server')
            self.connected_event.clear()

        @self.client.event(namespace=self.namespace)
        async def __disconnect_final():
            self.connected = False
            self.connected_event.set()

        @self.client.on('*')
        async def on_any_event(event, data):
            await self.on_event_callback(event, data)

        await self.client.connect(
            url, headers=headers, auth=auth, transports=transports,
            namespaces=[namespace], socketio_path=socketio_path,
            wait_timeout=wait_timeout)

    @property
    def sid(self):
        return self.client.get_sid(self.namespace) if self.client else None

    @property
    def transport(self):
        return self.client.transport if self.client else ''

    async def disconnect(self):
        if self.connected:
            await self.client.disconnect()
            self.client = None
            self.connected = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()


class OrdrClient(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.render_queue = []
        self.websocket = None
        self.base_url = 'https://apis.issou.best/'
        self.devmode = kwargs.pop('devmode', False)

    async def websocket_event_handler(self, event, data):
        if event == 'render_added_json':
            return

        if event == 'render_progress_json':
            return

        if event == 'render_done_json':
            return

        if event == 'render_failed_json':
            return

        raise Exception('Unhandled event')

    async def set_websocket(self, ws):
        self.websocket = ws
        await self.websocket.connect('https://apis.issou.best', socketio_path='/ordr/ws',
                                     on_event_callback=self.websocket_event_handler)

    async def upload_replay(self, ):
        return
