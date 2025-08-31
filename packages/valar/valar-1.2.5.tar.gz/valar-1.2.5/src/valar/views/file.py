import json

from minio import Minio

from ..classes.valar_response import ValarResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import QueryDict

from ..dao import Dao, OrmDao
from ..dao.engine import ValarEngine


def save_file(request, db, entity):
    params: QueryDict = request.POST.dict()
    _id, prop, field = (params.get(key) for key in ['id', 'prop', 'field'])
    file: InMemoryUploadedFile = request.FILES['file']
    dao = Dao(entity, db)
    engine = ValarEngine().get_minio_bucket(entity)
    item = dao.find_one(_id)
    if engine is None or item is None:
        return ValarResponse(False)
    old_value = getattr(item, prop)
    if old_value:
        engine.remove(old_value.name)
    object_name = engine.get_object_name(_id, prop, file.name)
    path = engine.upload(object_name, file.read())
    setattr(item, prop, path)
    if field:
        setattr(item, field, file.name)
    item.save()
    return ValarResponse(path)


def remove_file(request, db, entity):
    body = json.loads(request.body)
    _id, prop, field = (body.get(key) for key in ['id', 'prop', 'field'])
    dao = Dao(entity, db)
    item = dao.find_one(_id)
    engine = ValarEngine().get_minio_bucket(entity)
    if engine is None or item is None:
        return ValarResponse(False)
    old_value = getattr(item, prop)
    if old_value:
        engine.remove(old_value.name)
    setattr(item, prop, None)
    if field:
        setattr(item, field, None)
    item.save()
    return ValarResponse(True)
