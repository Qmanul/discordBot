import asyncio

from socketio import AsyncClient


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

    async def connect(self, url, headers=None, auth=None, transports=None,
                      namespace='/', socketio_path='socket.io',
                      wait_timeout=5):
        if headers is None:
            headers = {}
        if self.connected:
            raise RuntimeError('Already connected')
        self.namespace = namespace
        self.input_buffer = []
        self.input_event.clear()
        self.client = AsyncClient(*self.client_args, **self.client_kwargs)

        @self.client.event(namespace=self.namespace)
        def connect():  # pragma: no cover
            print('connection established')
            self.connected = True
            self.connected_event.set()

        @self.client.event(namespace=self.namespace)
        def disconnect():  # pragma: no cover
            print('disconnected from server')
            self.connected_event.clear()

        @self.client.event(namespace=self.namespace)
        def __disconnect_final():  # pragma: no cover
            self.connected = False
            self.connected_event.set()

        @self.client.on('render_done_json')
        def on_message(data):
            print(f'render done {data}')

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
