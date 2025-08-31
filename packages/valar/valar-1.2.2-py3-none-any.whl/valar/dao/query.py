from django.db.models import Q
from functools import reduce


class Query:

    def __init__(self, conditions: list, orders=None):
        self.is_empty = conditions is None or len(conditions) == 0
        self.orders = orders or {'sort': -1}
        self.conditions = [{'includes': {}, 'excludes': {}}] if self.is_empty else conditions

    def orm(self):
        orders = __translate_orders__(self.orders)
        includes = __translate_orm_condition__(self.conditions, 'includes')
        excludes = __translate_orm_condition__(self.conditions, 'excludes')
        return includes, excludes, orders

    def mon(self):
        finder = {}
        return finder, self.orders


def __fun__(x, y): return x | y


def __translate_orders__(orders):
    array = []
    for key in orders:
        value = orders.get(key)
        prefix = '-' if value == -1 else ''
        array.append(f'{prefix}{key}')
    return array


def __translate_orm_condition__(conditions, _type):
    return reduce(__fun__, [Q(**cond.get(_type, {})) for cond in conditions])
