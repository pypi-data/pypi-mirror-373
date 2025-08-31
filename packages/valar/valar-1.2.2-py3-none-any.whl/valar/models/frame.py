from django.db import models
from .core import VModel, VTree


class MetaFieldTool(VTree):
    name = models.CharField(max_length=255, null=True, verbose_name='名称')
    code = models.CharField(max_length=100, unique=True, null=True, verbose_name='代码')  #
    align = models.CharField(max_length=10, null=True, verbose_name='对齐方式')

    class Meta:
        verbose_name = '元数据字段工具'


#
#

class MetaFieldDomain(VModel):
    name = models.CharField(max_length=255, unique=True, null=True, verbose_name='名称')
    tools = models.ManyToManyField(to=MetaFieldTool, verbose_name='工具集')
    default = models.ForeignKey(
        to=MetaFieldTool, null=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='默认工具')

    class Meta:
        verbose_name = '元数据字段类型'
