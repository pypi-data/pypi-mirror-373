import json
import time
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpRequest
import threading
from .consumer import VALAR_CHANNEL_GROUP


class Channel:

    def __init__(self, request: HttpRequest):
        body = json.loads(request.body)
        self.handler = body.get('handler')
        self.url = body.get('url')
        self.auth = body.get('auth')
        self.broadcast = body.get('broadcast')
        self.data = body.get('data')

    def to_dict(self, status, payload):
        data = {
            'handler': self.handler,
            'url': self.url,
            'auth': self.auth,
            'broadcast': self.broadcast,
            'timestamp': datetime.now().timestamp()
        }
        if status:
            data.update({'status': status})
        if payload:
            data.update({'payload': payload})
        return data


class Sender:

    def __init__(self, request: HttpRequest):
        self.client = request.headers.get('CLIENT')
        self.uid = request.session.get('UID')
        self.group_send = async_to_sync(get_channel_layer().group_send)


class ValarChannelSender(Sender):

    def __init__(self, request: HttpRequest, interval=1):
        super().__init__(request)
        self.__channel__ = Channel(request)
        self.data = self.__channel__.data
        self.__payload__ = None
        self.__loading__ = False
        self.__thread__ = None
        self.__lock__ = threading.Lock()
        self.__interval__ = interval
        if self.__channel__.auth and not self.uid:
            raise Exception('Unauthorized!')

    def _run(self):
        while self.__loading__:
            self.__emit__()
            time.sleep(self.__interval__)

    def start(self):
        if self.__loading__:
            return  # 避免重复启动
        self.__payload__ = None
        self.__loading__ = True
        self.__emit__('start')
        self.__thread__ = threading.Thread(target=self._run, daemon=True)
        self.__thread__.start()

    def stop(self):
        self.__payload__ = None
        self.__loading__ = False
        self.__emit__('stop')
        if self.__thread__:
            self.__thread__.join()
            self.__thread__ = None

    def load(self, payload):
        with self.__lock__:
            self.__payload__ = payload

    def done(self, payload):
        self.__emit__('done', payload)

    def __emit__(self, status='proceed', data=None):
        scope = 'broadcast' if self.__channel__.broadcast else 'client'
        body = {
            'type': f'{scope}.emit',
            'data': self.__channel__.to_dict(status, data or self.__payload__),
            'clients': [self.client],
            'users': []
        }
        self.group_send(VALAR_CHANNEL_GROUP, body)


class ValarSocketSender(Sender):
    def __init__(self, request: HttpRequest):
        super().__init__(request)
        if self.uid:
            body = {'type': 'broadcast.emit', 'uid': self.uid, 'client': self.client}
            self.group_send(VALAR_CHANNEL_GROUP, body)

    def to_users(self, payload, users: list):
        body = {'type': 'user.emit', 'data': payload, 'users': users}
        self.group_send(VALAR_CHANNEL_GROUP, body)

    def to_clients(self, payload, clients: list):
        body = {'type': 'client.emit', 'data': payload, 'clients': clients}
        self.group_send(VALAR_CHANNEL_GROUP, body)

    def broadcast(self, payload):
        body = {'type': 'broadcast.emit', 'data': payload}
        self.group_send(VALAR_CHANNEL_GROUP, body)
