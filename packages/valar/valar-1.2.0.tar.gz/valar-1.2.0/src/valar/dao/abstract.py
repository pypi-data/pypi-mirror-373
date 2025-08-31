from abc import ABC, abstractmethod

from bson import ObjectId

from ..dao.engine import ValarEngine


class AbstractField(ABC):
    db = None
    entity = None
    prop = None
    label = None
    domain = None
    refer = None

    @abstractmethod
    def to_dict(self):
        pass


class AbstractDao(ABC):
    engine = ValarEngine()
    db = None
    entity = None
    name = None
    is_tree = False
    fields = {}

    def props(self, domain=None):
        return [prop for prop, field in self.fields.items() if field.domain == domain or domain is None]

    def full_props(self):
        return {
            prop: {
                "prop": prop,
                "domain": field.domain,
                "label": field.label,
            }
            for prop, field in self.fields.items()
        }

    def get_meta_field(self, prop) -> AbstractField:
        return self.fields[prop]

    @abstractmethod
    def save_one(self, item, with_id=False):
        pass

    @abstractmethod
    def save_many(self, array: list):
        pass

    @abstractmethod
    def values(self, conditions, props):
        pass

    @abstractmethod
    def delete_one(self, _id):
        pass

    @abstractmethod
    def find_one(self, _id):
        pass

    @abstractmethod
    def find(self, conditions=None, orders=None, size=0, page=1):
        pass

    @abstractmethod
    def update(self, template, conditions):
        pass

    @abstractmethod
    def delete(self, conditions=None) -> list:
        pass

    @abstractmethod
    def serialize(self, o, code=None):
        pass

    @abstractmethod
    def tree(self, root, conditions=None):
        pass

    def search(self, includes=None, excludes=None, orders=None):
        conditions = [{"includes": includes or {}, "excludes": excludes or {}}]
        results, _ = self.find(conditions, orders)
        return results

    def object_id(self, _id):
        try:
            return int(_id) if self.db == 'orm' else ObjectId(_id)
        except Exception:
            return None

    # @abstractmethod
    # def values(self, props, conditions, orders=None):
    #     pass
    #
    # @abstractmethod
    # def group(self, props, conditions, orders=None):
    #     pass
    #
    # @abstractmethod
    # def count(self, props, conditions):
    #     pass
