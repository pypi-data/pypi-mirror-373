import datetime
import json

from django.core.paginator import Paginator

from .abstract import AbstractDao
from .query import Query
from django.db.models import ManyToOneRel, ForeignKey, ManyToManyRel, ManyToManyField, OneToOneField, OneToOneRel
from django.db.models import QuerySet
from django.db.models import Manager
from django.db.models.fields.files import FieldFile
from django.forms import FileField

from ..dao.orm_field import OrmField
from ..models.core import VTree, VModel
from ..models.meta import MetaField


class OrmDao(AbstractDao):

    def __init__(self, entity):
        model = self.engine.get_orm_model(entity)
        meta = getattr(model, '_meta')
        self.minio = self.engine.get_minio_bucket(entity)
        self.db = 'orm'
        self.entity = entity
        self.name = meta.verbose_name
        self.is_tree = issubclass(model, VTree)
        self.manager: Manager = model.objects
        fields = {}
        model_fields = meta.get_fields()
        for model_field in model_fields:
            meta_field = OrmField(entity, model_field, self.is_tree)
            fields[meta_field.prop] = meta_field
        self.fields = fields

    def save_many(self, array: list):
        pass

    def values(self, conditions, props: list):
        query_set, _ = self.find(conditions)
        if 'id' not in props:
            props.append('id')
        return list(query_set.values(*props))

    def save_one(self, item, with_id=False):
        oid, simple_item, complex_item = self.__detach_item__(item)
        query_set = self.manager.filter(id=oid) if oid else []
        if len(query_set):
            simple_item['modify_time'] = datetime.datetime.now()
            query_set.update(**simple_item)
            bean = query_set.first()
        else:
            if oid:
                simple_item.update({'id': oid})
            bean = self.manager.create(**simple_item)
            if simple_item.get('sort') is None:
                bean.sort = bean.id
                bean.save()
        self.__save_complex_field__(complex_item, bean)
        bean.save()
        return bean

    def delete_one(self, _id):
        oid = self.object_id(_id)
        flag = oid is not None
        if flag:
            query_set = self.manager.filter(id=oid)
            paths = self.__get_file_paths__(query_set)
            for path in paths:
                self.minio.remove(path)
            query_set.delete()
        return flag

    def find_one(self, _id):
        oid = self.object_id(_id)
        return self.manager.filter(id=oid).first() if oid is not None else None

    def find(self, conditions=None, orders=None, size=0, page=1):
        includes, excludes, orders = Query(conditions, orders).orm()
        query_set = self.manager.filter(includes).exclude(excludes).order_by(*orders)
        total = query_set.count()
        if size:
            paginator = Paginator(query_set, size)
            query_set = paginator.page(page).object_list
        return query_set, total

    def update(self, template, conditions):
        flag = template is not None and len(template.keys())
        if flag:
            oid, simple_item, complex_item = self.__detach_item__(template)
            query_set, total = self.find(conditions)
            query_set.update(**simple_item)
        return flag

    def delete(self, conditions=None) -> list:
        query_set, total = self.find(conditions)
        query_set.delete()
        return self.__get_file_paths__(query_set)

    def serialize(self, o, code=None):
        return self.__to_dict__(o, code) if isinstance(o, QuerySet) else o.full()

    def tree(self, root, conditions=None):
        all_set, _ = self.find()
        if Query(conditions).is_empty:
            return all_set
        values = all_set.values('id', 'pid')
        mapping = {item['id']: item['pid'] for item in values}
        results, _ = self.find(conditions)
        id_set = {root}
        for item in results:
            _id = item.id
            route = []
            while _id is not None:
                route.append(_id)
                _id = mapping.get(_id)
            if root in route:
                id_set.update(route)
        return all_set.filter(id__in=id_set).order_by('-sort')

    """ 以下为私有方法 """

    def __detach_item__(self, item):
        _id = item.get('id')
        if _id:
            del item['id']
        simple_item = {}
        complex_item = {}
        for prop in item:
            meta_field = self.fields.get(prop)
            if meta_field:
                value = item.get(prop)
                if meta_field.domain in ['ManyToOneRel', 'ManyToManyField', 'ManyToManyRel']:
                    complex_item[prop] = value
                elif meta_field.domain in ['OneToOneRel', 'OneToOneField', 'FileField']:
                    complex_item[prop] = value
                else:
                    simple_item[prop] = value
        return self.object_id(_id), simple_item, complex_item

    def __save_complex_field__(self, complex_item, bean):
        for prop in complex_item:
            value = complex_item[prop]
            model_field = self.fields[prop].model_field
            clazz = type(model_field)
            if clazz == ManyToManyField:
                m2m = getattr(bean, prop)
                m2m.clear()
                m2m.add(*value)
            elif clazz == ManyToOneRel:
                getattr(bean, model_field.get_accessor_name()).clear()
                remote_model: VModel = model_field.related_model
                new_set: QuerySet = remote_model.objects.filter(id__in=value)
                remote_field: ForeignKey = model_field.remote_field
                k = remote_field.get_attname()
                new_set.update(**{k: bean.id})
            elif clazz == ManyToManyRel:
                getattr(bean, model_field.get_accessor_name()).clear()
                remote_model: VModel = model_field.related_model
                remote_items: QuerySet = remote_model.objects.filter(id__in=value)
                remote_field: ManyToManyField = model_field.remote_field
                remote_field_prop = remote_field.get_attname()
                for _bean in remote_items:
                    bean_set = getattr(_bean, remote_field_prop)
                    bean_set.add(bean)
            elif clazz == OneToOneRel and value is not None:
                remote_model: VModel = model_field.related_model
                remote_field: OneToOneField = model_field.remote_field
                remote_field_prop = remote_field.get_attname()
                _bean = remote_model.objects.get(id=value)
                __bean = remote_model.objects.filter(**{remote_field_prop: bean.id}).first()
                if __bean:
                    setattr(__bean, remote_field_prop, None)
                    __bean.save()
                setattr(_bean, remote_field_prop, bean.id)
                _bean.save()
            elif clazz == OneToOneField and value is not None:
                __bean = model_field.model.objects.filter(**{prop: value}).first()
                if __bean:
                    setattr(__bean, prop, None)
                    __bean.save()
                setattr(bean, prop, value)
            elif clazz == FileField:
                file_name, _bytes = value
                field_file: FieldFile = getattr(bean, prop)
                if field_file:
                    path = field_file.name
                    self.minio.remove(path)
                object_name = self.minio.get_object_name(bean.id, prop, file_name)
                path = self.minio.upload(object_name, _bytes) if _bytes else None
                setattr(bean, prop, path)

    def __get_file_paths__(self, query_set: QuerySet):
        props = self.props('FileField')
        if len(props):
            items = query_set.values(*props)
            paths = []
            for item in items:
                paths += [i for i in item.values() if i]
            return [path for path in paths if path]
        return []

    def __to_dict__(self, query_set: QuerySet, code=None):
        meta_fields = self.fields.values()
        # 简单字段取值
        simple_props = [field.prop for field in meta_fields if field.domain not in __referred_domains__]
        custom_props = __get_custom_props__(self.entity, code)
        results = list(query_set.filter().values(*[*simple_props, *custom_props]))
        __set_simple_values__(meta_fields, results)
        # 关系型字段取值
        mapping = {row['id']: row for row in results}
        referred_fields = [field for field in meta_fields if field.domain in __referred_domains__]
        pks = mapping.keys()
        for meta_field in referred_fields:
            manager: Manager = query_set.model.objects
            qs = manager.filter(id__in=pks)
            __linkage__(meta_field, qs, mapping)
        return results


""" 以下为静态方法和变量 """

__multiple_domains__ = ['ManyToOneRel', 'ManyToManyField', 'ManyToManyRel']
__referred_domains__ = [*__multiple_domains__, 'OneToOneRel', 'OneToOneField', 'ForeignKey']
__omit_field_props__ = ['create_time', 'modify_time', 'saved', 'sort']
__data_props_formatting__ = {'DateField': '%Y-%m-%d', 'DateTimeField': '%Y-%m-%d %H:%M:%S', 'TimeField': '%H:%M:%S'}


def __get_custom_props__(entity, code='default'):
    field_set = MetaField.objects.filter(view__code=code, view__meta__entity=entity, domain='Custom').values('prop')
    return [item['prop'] for item in field_set if item['prop'] is not None]


def __set_simple_values__(fields, values):
    date_props_mapping = {}
    json_props = []
    for field in fields:
        if isinstance(field, OrmField):
            prop = field.prop
            domain = field.domain
        else:
            prop = field.name
            domain = type(field).__name__
        if domain in __data_props_formatting__.keys():
            date_props_mapping[prop] = __data_props_formatting__[domain]
        elif domain == 'JSONField':
            json_props.append(prop)
    for row in values:
        for prop, formating in date_props_mapping.items():
            if row.get(prop):
                row[prop] = row[prop].strftime(formating)
        for prop in json_props:
            row[prop] = json.loads(row[prop]) if type(row[prop]) is str else row[prop]


def __get_related_props__(fields):
    def fun(field): return type(field).__name__ not in __referred_domains__ and field.name not in __omit_field_props__

    return [field.name for field in fields if fun(field)]


def __linkage__(meta_field: OrmField, query_set: QuerySet, mapping):
    model_field = meta_field.model_field
    prop = model_field.name
    multiple = meta_field.domain in __multiple_domains__

    # 获取级联关系的键索引
    ref_prop = f'{prop}__id'
    edges = query_set.exclude(**{f'{ref_prop}__isnull': True}).values('id', ref_prop)
    if multiple:
        related_primary_keys = set()
        results_mapping = {}
        for edge in edges:
            _id, rid = edge['id'], edge[ref_prop]
            related_primary_keys.add(rid)
            array = results_mapping.get(_id, [])
            array.append(rid)
            results_mapping[_id] = array
    else:
        results_mapping = {row['id']: row[ref_prop] for row in edges if row[ref_prop]}
        related_primary_keys = set(results_mapping.values())

    # 获取级联关系从属方的数据
    related_model = model_field.related_model
    related_fields = related_model._meta.get_fields()
    related_props = __get_related_props__(related_fields)
    related_values = list(related_model.objects.filter(id__in=related_primary_keys).values(*related_props))
    __set_simple_values__(related_fields, related_values)
    related_mapping = {item['id']: item for item in related_values}

    # 将从属方的数据绑定在主数据上
    for _id in mapping:
        row = mapping[_id]
        if multiple:
            keys = results_mapping.get(_id, [])
            items = [related_mapping[pid] for pid in keys]
            row[prop] = keys
            row[f'{prop}_set'] = items
        else:
            key = results_mapping.get(_id)
            item = related_mapping.get(key) if key else None
            row[prop] = item
            row[f'{prop}_id'] = key
