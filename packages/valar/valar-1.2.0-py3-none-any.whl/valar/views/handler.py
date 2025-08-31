from ..channels.counter import Counter
from ..channels.sender import ValarChannelSender
from ..dao import Dao
from ..dao.engine import ValarEngine


def batch_handler(sender: ValarChannelSender):
    data = sender.data
    entity, db, method = data.get("entity"), data.get("db"), data.get("method")
    dao = Dao(entity, db)
    body = {"method": method}
    if method == 'save_many':
        array = data.get("array", [])
        counter = Counter(array)
        keys = []
        for item in array:
            item.update({'saved': True})
            bean = dao.save_one(item)
            keys.append(bean.id)
            payload = counter.tick()
            sender.load(payload)
        body.update({'keys': keys})
        sender.done(body)
    elif method == 'delete_many':
        conditions = data.get("conditions", [])
        paths = dao.delete(conditions)
        counter = Counter(len(paths))
        minio = ValarEngine().get_minio_bucket(entity)
        for path in paths:
            minio.remove(path)
            payload = counter.tick()
            sender.load(payload)
        sender.done(body)
