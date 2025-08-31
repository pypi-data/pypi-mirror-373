import time

from ..valar.channels.counter import Counter
from ..valar.channels.sender import ValarChannelSender


def valar_test_handler(sender: ValarChannelSender):
    data = sender.data
    length = data.get('length', 100)
    counter = Counter(length)
    for i in range(length):
        time.sleep(0.1)
        tick = counter.tick()
        tick.update({'name': 'test1'})
        sender.load(tick)
