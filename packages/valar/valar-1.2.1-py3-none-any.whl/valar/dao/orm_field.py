from deepmerge import always_merger
from django.db.models import ManyToOneRel, ForeignKey, ManyToManyRel, ManyToManyField, OneToOneField, OneToOneRel
from django.db.models import IntegerField, BooleanField, FloatField, TextField, CharField
from django.db.models import FileField, JSONField
from django.db.models import DateTimeField, TimeField, DateField
from django.db.models.options import Options

from ..dao.abstract import AbstractField
from ..dao.frame import meta_field_domain_mapping, meta_field_tool_mapping
from ..models.core import VTree


class OrmField(AbstractField):

    def __init__(self, entity, model_field, is_tree):
        self.db = 'orm'
        self.entity = entity
        self.model_field = model_field
        self.is_tree = is_tree
        self.not_null = not model_field.null
        self.clazz = type(model_field)
        self.multiple = self.clazz in [ManyToOneRel, ManyToManyField, ManyToManyRel]
        self.prop = self.__prop__()
        self.domain = self.__domain__()
        self.model = self.__model__()
        self.label = self.__label__()
        self.tool = meta_field_domain_mapping.get(self.domain, 'none')
        self.column_width = column_width(self.domain, self.tool)
        self.refer = self.__refer__()
        self.format = self.__formating__()

    def to_dict(self):
        _field = {
            "prop": self.prop,
            "label": self.label,
            "name": self.label,
            "domain": self.domain,
            "refer": self.refer,
            "format": self.format,
            "not_null": self.not_null,
            "column_width": self.column_width,
            "tool": self.tool,
            "disabled": False,
        }
        if self.is_tree:
            if self.prop in ['pid', 'isLeaf']:
                # _field['hide_on_table'] = True
                _field['hide_on_form'] = True
                _field['hide_on_form_branch'] = True
                _field['hide_on_form_leaf'] = True
            elif self.prop in ['icon']:
                _field['tool'] = 'icon'
        elif self.refer['isTree']:
            _field['tool'] = 'tree'
        return _field

    def __label__(self):
        return self.model._meta.verbose_name \
            if self.clazz in [ManyToOneRel, ManyToManyField, ManyToManyRel, OneToOneRel, OneToOneField] \
            else self.model_field.verbose_name

    def __model__(self):
        return self.model_field.related_model \
            if self.clazz in [ManyToOneRel, ManyToManyField, ManyToManyRel, OneToOneRel, OneToOneField, ForeignKey] \
            else None

    def __domain__(self):
        return self.clazz.__name__ \
            if self.clazz in [ManyToOneRel, ManyToManyField, ManyToManyRel, OneToOneRel, OneToOneField] \
            else self.model_field.get_internal_type()

    def __prop__(self):
        return self.model_field.name + "_id" \
            if self.clazz in [ForeignKey, OneToOneRel, OneToOneField] \
            else self.model_field.name

    def __refer__(self):
        refer = {
            "entity": None, "db": self.db,
            "value": "id", "label": 'name', "display": "id",
            "multiple": self.multiple, "strict": False, "remote": False,
            "includes": {}, "excludes": {},
            "root": 0, "isTree": False
        }
        if self.model:
            meta: Options = getattr(self.model, '_meta')

            refer['entity'] = '%s.%s' % (meta.app_label, self.model.__name__)
            refer['isTree'] = issubclass(self.model, VTree)
        return refer

    def __formating__(self):
        _format = {
            # 文本
            "maxlength": None,
            "type": 'text',

            # 数值
            "min": None,
            "max": None,
            "step": 1,
            "precision": None,
            "step_strictly": False,

            # 日期
            "frequency": "date",

            # 文件
            "maximum": 5,
            "accept": [],
            "width": 800,
            "height": None,
            "file_name_field": None,
            "locked": False,

            # 集合
            "set": {},
            "multiple": False
        }
        if self.clazz == CharField:
            _format['maxlength'] = self.model_field.max_length
            _format['$maxlength'] = self.model_field.max_length
        if self.clazz == TextField:
            _format['type'] = "textarea"
        elif self.clazz == DateTimeField:
            _format['frequency'] = "datetime"
        elif self.clazz == IntegerField:
            _format['precision'] = 0
            _format['step_strictly'] = True
        return _format


def column_width(domain, tool):
    if domain in ['BooleanField', 'FileField', 'JSONField']:
        return 80
    elif domain in ['DateField', 'DateTimeField', 'TimeField']:
        return 120
    elif domain in ['ManyToManyRel', 'ManyToManyRel', 'ManyToOneRel']:
        return 80
    elif domain in ['TextField']:
        return 80 if tool == 'rich' else 0
    return 0
