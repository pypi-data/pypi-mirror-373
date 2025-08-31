import json

from .handler import batch_handler
from ..channels.executer import execute_channel
from ..channels.sender import ValarChannelSender
from ..classes.valar_response import ValarResponse
from ..dao import Dao


async def batch(request):
    sender = ValarChannelSender(request)
    await execute_channel(batch_handler, sender)
    return ValarResponse(True)


def save_one(request, db, entity):
    item = json.loads(request.body)
    dao = Dao(entity, db)
    bean = dao.save_one(item)
    item = dao.serialize(bean)
    return ValarResponse(item)


def values(request, db, entity):
    body = json.loads(request.body)
    dao = Dao(entity, db)
    conditions = body.get('conditions', [])
    props = body.get('props', ['id'])
    array = dao.values(conditions, props)
    return ValarResponse(array)


def delete_one(request, db, entity):
    body = json.loads(request.body)
    _id = body['id']
    dao = Dao(entity, db)
    flag = dao.delete_one(_id)
    return ValarResponse(flag)


def find_one(request, db, entity):
    body = json.loads(request.body)
    _id = body['id']
    dao = Dao(entity, db)
    bean = dao.find_one(_id)
    item = dao.serialize(bean)
    return ValarResponse(item)


def find(request, db, entity):
    conditions = json.loads(request.body)
    dao = Dao(entity, db)
    results, _ = dao.find(conditions)
    results = dao.serialize(results)
    return ValarResponse(results)


def update(request, db, entity):
    body = json.loads(request.body)
    conditions = body.get('conditions', [])
    template = body.get('template')
    dao = Dao(entity, db)
    flag = dao.update(template, conditions)
    return ValarResponse(flag)


def search(request, db, entity):
    body = json.loads(request.body)
    _type = body.get('type')
    orders = body.get('orders')
    size = body.get('size')
    page = body.get('page')
    root = body.get('root')
    code = body.get('code', 'default')
    conditions = body.get('conditions')
    dao = Dao(entity, db)

    if _type == 'tree':
        query_set = dao.tree(root, conditions)
        total = query_set.count()
    else:
        query_set, total = dao.find(conditions, orders, size, page)
    results = dao.serialize(query_set, code)

    return ValarResponse({
        "results": results,
        "type": _type,
        "total": total,
        "root": root
    })
