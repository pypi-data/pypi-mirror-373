import copy

from deepmerge import always_merger
from django.conf import settings

from ..dao.defaults.field_keys_default import meta_field_key_defaults
from ..dao.defaults.field_values_default import meta_field_value_defaults
from ..dao.defaults.view_defaults import meta_view_default_values
from ..dao.abstract import AbstractDao
from ..dao.frame import meta_field_tool_mapping
from ..dao.mon_dao import MonDao
from ..dao.orm_dao import OrmDao
from ..dao.orm_field import column_width
from ..models.frame import MetaFieldDomain
from ..models.meta import Meta, MetaView


class ValarMeta:
    def __init__(self, db, entity, code):
        self.entity = entity
        self.db = db
        self.dao: AbstractDao = MonDao(entity) if db == 'mon' else OrmDao(entity)
        self.code = code or 'default'

        meta_dao = OrmDao('valar.Meta')
        view_dao = OrmDao('valar.MetaView')
        field_dao = OrmDao('valar.MetaField')

        meta_item = {"entity": entity, 'db': db}
        meta: Meta = meta_dao.search(meta_item).first()
        if meta is None:
            meta_item.update({"name": self.dao.name, 'saved': True, 'tree': self.dao.is_tree})
            meta = meta_dao.save_one(meta_item)
        self.meta = meta

        # load_view
        view_item = {"code": self.code, "meta_id": meta.id}
        view: MetaView = view_dao.search(view_item).first()
        if view is None:
            self.__initial_view__(view_item)
            view = view_dao.save_one(view_item)
        self.view = view

        # load_fields
        if view.metafield_set.count() == 0:
            _fields = self.__initial_fields__()
            for _field in _fields:
                if _field['prop'] not in ['sort', 'create_time', 'modify_time', 'saved']:
                    _field.update({'view_id': view.id, "saved": True})
                    field_dao.save_one(_field)

    def meta_view(self):
        _view = self.view.json()
        meta = self.meta.json()
        name, entity = meta['name'], meta['entity']
        fields = self.view.metafield_set.all().order_by('-sort')
        _fields = {}
        _minio = settings.MINIO_ROOT if hasattr(settings, 'MINIO_ROOT') else '/minio'
        for field in fields:
            _field = field.json(entity=entity, code=self.code, db='orm', minio=_minio)
            align, tool, width, domain = _field['align'], _field['tool'], _field['column_width'], _field['domain']
            _field['align'] = align if align else meta_field_tool_mapping.get(tool, 'left')
            _field['column_width'] = width if width else column_width(domain, tool)

            _fields[field.prop] = _field

        _minio = settings.MINIO_ROOT if hasattr(settings, 'MINIO_ROOT') else '/minio'
        _view.update({
            '$minio': _minio,
            '$db': 'orm',
            '$entity': entity,
            '$code': self.code,
            '$meta_name': name,
            '$isTree': self.dao.is_tree,
            '$fields': _fields,
            '$modes': self.dao.full_props()
        })
        return _view

    """ 默认的view设置 """

    def __initial_view__(self, view_item: dict):
        default_view = meta_view_default_values.get(self.entity, {})
        default_values = copy.deepcopy(default_view.get('__init__', {}))
        code_values = copy.deepcopy(default_view.get(self.code, {}))
        view_item.update({
            "name": self.code.upper(),
            "saved": True,
            "property": {
                "value": "id",
                "label": "name",
                "display": "id",
                "sort": "sort",
                "disabled": "disabled",
                "isLeaf": "isLeaf",
                "icon": "icon",
                "children": "children",
                "pid": "pid",
            }
        })
        values = always_merger.merge(default_values, code_values)
        view_item.update(values)

    def __initial_fields__(self):
        default_keys = meta_field_key_defaults.get(self.entity, {})
        method, array = default_keys.get(self.code, ('omit', []))

        def fun(prop):
            return prop not in array if method == 'omit' else prop in array

        props = [prop for prop in self.dao.props() if fun(prop)]
        if method == 'pick':
            props = [prop for prop in array if prop in props]

        default_values = copy.deepcopy(meta_field_value_defaults.get(self.entity, {}))
        init_values = default_values.get('__init__', {})
        code_values = default_values.get(self.code, {})
        default_fields = always_merger.merge(init_values, code_values)

        fields = []
        for prop in props:
            field = self.dao.get_meta_field(prop)
            field_json = field.to_dict()
            default_field = default_fields.get(prop, {})
            always_merger.merge(field_json, default_field)
            fields.append(field_json)
        fields.reverse()
        return fields
