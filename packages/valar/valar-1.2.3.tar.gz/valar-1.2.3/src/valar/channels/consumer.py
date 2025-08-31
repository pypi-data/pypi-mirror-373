from channels.generic.websocket import AsyncJsonWebsocketConsumer

VALAR_CHANNEL_GROUP = 'VALAR'


class ValarConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self):
        self.client = None
        self.uid = None
        super().__init__()

    async def connect(self):
        params = self.scope['url_route']['kwargs']
        self.client = params.get('client')
        await self.channel_layer.group_add(VALAR_CHANNEL_GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(VALAR_CHANNEL_GROUP, self.channel_name)
        await self.close(code)

    async def receive_json(self, data, *args, **kwargs):
        pass

    async def user_emit(self, event):
        users: list = event.get('users', [])
        data = event.get('data', {})
        if self.uid in users:
            await self.send_json(data)

    async def client_emit(self, event):
        clients: list = event.get('clients', [])
        data = event.get('data', {})
        if self.client in clients:
            await self.send_json(data)

    async def broadcast_emit(self, event):
        data = event.get('data', {})
        await self.send_json(data)

    async def register_emit(self, event):
        uid = event.get('uid', )
        client = event.get('client')
        if self.client == client:
            self.uid = uid
