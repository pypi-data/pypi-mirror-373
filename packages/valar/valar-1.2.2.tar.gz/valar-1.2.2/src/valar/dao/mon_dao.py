from pymongo.synchronous.collection import Collection
from pymongo.results import InsertOneResult
from pymongo.synchronous.cursor import Cursor

from collections import defaultdict

from .query import Query
from ..dao.abstract import AbstractDao
from ..dao.mon_field import MonField

domain_mapping = {
    'ObjectId': ('BigAutoField', 'none'),
    'int': ('CharField', 'number'),
    'str': ('TextField', 'text'),
    'float': ('CharField', 'number'),
    'bool': ('BooleanField', 'boolean'),
}


class MonDao(AbstractDao):

    def __init__(self, entity):
        self.db = 'mon'
        self.entity = entity
        self.name = entity
        self.manager: Collection = self.engine.get_mongo_collection(entity)
        self.is_tree = False
        fields = {}
        for prop, domain, tool in self.__analyze_field_types__():
            fields[prop] = MonField(entity, prop, domain, tool)
        self.fields = fields

    def __analyze_field_types__(self):
        array = []
        type_map = defaultdict(set)
        cursor = self.manager.find().limit(1000)
        for doc in cursor:
            for key, value in doc.items():
                type_map[key].add(type(value).__name__)
        for prop, domains in dict(type_map).items():
            domain, tool = domain_mapping[domains.pop()]
            prop = 'id' if prop == '_id' else prop
            array.append((prop, domain, tool))
        return array

    def __detach_item__(self, item):
        _id = item.get('id')
        if _id:
            del item['id']
            return self.object_id(_id), item
        else:
            return None, item

    def save_many(self, array: list):
        self.manager.insert_many(array)

    def values(self, conditions, props):
        return None

    def save_one(self, item, with_id=False):
        oid, item = self.__detach_item__(item)
        if oid:
            self.manager.update_one({'_id': oid}, {'$set': item})
        else:
            bean: InsertOneResult = self.manager.insert_one(item)
            oid = bean.inserted_id
            self.manager.update_one({'_id': oid}, {'$set': {'sort': str(oid)}})
        return self.manager.find_one({'_id': oid})

    def delete_one(self, _id):
        oid = self.object_id(_id)
        flag = oid is not None
        if flag:
            self.manager.delete_one({'_id': oid})
        return flag

    def find_one(self, _id):
        oid = self.object_id(_id)
        return self.manager.find_one({'_id': oid}) if oid else None

    def find(self, conditions=None, orders=None, size=0, page=1):
        finder, orders = Query(conditions, orders).mon()
        skip = (page - 1) * size
        total = self.manager.count_documents(finder)
        cursor = self.manager.find(finder).skip(skip).sort(orders)
        if size:
            cursor = cursor.limit(size)
        return cursor, total

    def update(self, template, conditions):
        flag = template is not None and len(template.keys())
        if flag:
            oid, item = self.__detach_item__(template)
            finder, _ = Query(conditions).mon()
            self.manager.update_many(finder, {'$set': item})
        return flag

    def delete(self, conditions=None) -> list:
        finder, _ = Query(conditions).mon()
        self.manager.delete_many(finder)
        return []

    def serialize(self, o, code=None):
        return [__to_item__(doc) for doc in o] if isinstance(o, Cursor) else __to_item__(o)

    def tree(self, root, conditions=None):
        pass


def __to_item__(o):
    o['id'] = str(o['_id'])
    del o['_id']
    return o
