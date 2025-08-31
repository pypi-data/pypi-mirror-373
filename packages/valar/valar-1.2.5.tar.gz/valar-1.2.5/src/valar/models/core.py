import json

from django.apps import AppConfig
from django.db import models
from django.db.models import ManyToOneRel, OneToOneRel, ManyToManyRel, ManyToManyField, UUIDField, FileField, \
    ForeignKey, OneToOneField, DateField, TimeField, DateTimeField, BigAutoField, JSONField
from django.db.models.options import Options


class VModel(models.Model):
    objects = models.Manager()
    sort = models.BigIntegerField(null=True, verbose_name='序号')
    name = models.CharField(max_length=50, null=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')
    disabled = models.BooleanField(default=False, verbose_name='禁用')
    saved = models.BooleanField(default=False, verbose_name='已保存')

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.full())

    def get_meta(self) -> Options:
        return getattr(self, '_meta')

    def get_entity(self):
        name = type(self).__name__
        config: AppConfig = self.get_meta().app_config
        return f'{config.label}.{name}'

    def json(self, *args, **kwargs):
        excludes = [ManyToOneRel, OneToOneRel, ManyToManyField, ManyToManyRel, UUIDField]
        fields = [field for field in self.get_meta().get_fields() if type(field) not in excludes]
        data = {}
        for field in fields:
            value = field.value_from_object(self)
            prop = field.name
            domain = type(field)
            if value is not None:
                if domain in [ForeignKey, OneToOneField]:
                    prop = f'{prop}_id'
                elif domain in [DateTimeField]:
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                elif domain in [DateField]:
                    value = value.strftime('%Y-%m-%d')
                elif domain in [TimeField]:
                    value = value.strftime('%H:%M:%S')
                elif domain in [FileField]:
                    value = value.name
                elif domain in [BigAutoField]:
                    value = value
            data[prop] = value
        data.update({f'${k}': v for k, v in kwargs.items()})
        return data

    def full(self):
        includes = [ManyToManyField, ManyToManyRel, ForeignKey, ManyToOneRel, OneToOneField, OneToOneRel]
        fields = [field for field in self.get_meta().get_fields() if type(field) in includes]
        data = self.json()
        for field in fields:
            prop = field.name
            domain = type(field)
            if domain in [ForeignKey, OneToOneField]:
                bean: VModel = getattr(self, prop)
                data[prop] = bean.json() if bean else None
            elif domain == OneToOneRel:
                print('OneToOneRel')
                pass
            elif domain == JSONField:
                data[prop] = json.loads(data[prop]) if type(data[prop]) is str else data[prop]
            elif domain in [ManyToManyField, ManyToManyRel, ManyToOneRel]:
                accessor = prop if domain == ManyToManyField else field.get_accessor_name()
                _set = getattr(self, accessor).all().order_by('-sort')
                data[prop] = [item.id for item in _set]
                data[f'{prop}_set'] = [item.json() for item in _set]

        return data


class VTree(VModel):
    pid = models.IntegerField(null=False, default=0, verbose_name='父节点')
    isLeaf = models.BooleanField(default=False, verbose_name='叶子节点')
    icon = models.CharField(max_length=255, null=True, verbose_name='图标')

    class Meta:
        abstract = True
