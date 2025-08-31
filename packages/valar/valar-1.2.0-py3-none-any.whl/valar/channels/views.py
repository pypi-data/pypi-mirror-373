from .executer import execute_channel
from .mapping import ChannelMapping
from .sender import ValarChannelSender
from ..classes.valar_response import ValarResponse


async def handel_channel(request, handler):
    sender = ValarChannelSender(request)
    method = ChannelMapping().get_handler(handler)
    await execute_channel(method, sender)
    return ValarResponse(True)
