from ..dao.abstract import AbstractDao
from ..dao.mon_dao import MonDao
from ..dao.orm_dao import OrmDao


class Dao(AbstractDao):

    def __init__(self, entity, db='orm'):
        self.dao = OrmDao(entity) if db == 'orm' else MonDao(entity)
        self.db = db
        self.entity = entity
        self.name = self.dao.name
        self.is_tree = self.dao.is_tree
        self.fields = self.dao.fields
        self.manager = self.dao.manager

    def save_many(self, array: list):
        self.dao.save_many(array)

    def save_one(self, item, with_id=False):
        return self.dao.save_one(item, with_id)

    def delete_one(self, _id):
        return self.dao.delete_one(_id)

    def find_one(self, _id):
        return self.dao.find_one(_id)

    def find(self, conditions=None, orders=None, size=0, page=1):
        return self.dao.find(conditions, orders, size, page)

    def values(self, conditions, props):
        return self.dao.values(conditions, props)

    def update(self, template, conditions):
        return self.dao.update(template, conditions)

    def delete(self, conditions=None) -> list:
        return self.dao.delete(conditions)

    def serialize(self, o, code=None):
        return self.dao.serialize(o, code)

    def tree(self, root, conditions=None):
        return self.dao.tree(root, conditions)
