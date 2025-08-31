import asyncio

from ..channels.sender import ValarChannelSender


async def execute_channel(method, sender: ValarChannelSender):
    thread = asyncio.to_thread(__execute__, method, sender)
    asyncio.create_task(thread)


def __execute__(method, sender: ValarChannelSender):
    sender.start()
    method(sender)
    sender.stop()
