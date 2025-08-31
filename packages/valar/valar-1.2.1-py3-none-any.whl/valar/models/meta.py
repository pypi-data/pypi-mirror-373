from django.db import models
from .core import VModel, VTree


class Meta(VModel):
    db = models.CharField(max_length=100, verbose_name='数据库', null=True)
    entity = models.CharField(max_length=100, verbose_name='数据源', null=True)
    name = models.CharField(max_length=50, verbose_name='实体别名', null=True)
    tree = models.BooleanField(default=False, verbose_name='是否树形')

    class Meta:
        verbose_name = '数据实体'
        unique_together = ('db', 'entity')


class MetaView(VModel):
    meta = models.ForeignKey('Meta', on_delete=models.CASCADE, verbose_name='元数据')
    property = models.JSONField(default=dict, verbose_name='属性')

    code = models.CharField(max_length=50, verbose_name='类视图', default='default ')
    name = models.CharField(max_length=50, verbose_name='视图名称', null=True)
    lock = models.BooleanField(default=False, verbose_name='锁定元数据')
    enable = models.BooleanField(default=True, verbose_name='是否启用')

    form_width = models.IntegerField(null=True, verbose_name='表单宽度')
    form_height = models.IntegerField(null=True, verbose_name='表单高度')
    table_width = models.IntegerField(null=True, verbose_name='表格宽度')
    table_height = models.IntegerField(null=True, verbose_name='表格高度')

    allow_search = models.BooleanField(default=True, verbose_name='检索功能')
    allow_order = models.BooleanField(default=True, verbose_name='排序功能')
    allow_insert = models.BooleanField(default=True, verbose_name='新增功能')

    allow_edit = models.BooleanField(default=True, verbose_name='编辑功能')
    allow_edit_on_form = models.BooleanField(default=True, verbose_name='表单编辑')
    allow_edit_on_cell = models.BooleanField(default=True, verbose_name='表内编辑')
    allow_edit_on_sort = models.BooleanField(default=True, verbose_name='移动功能')

    allow_remove = models.BooleanField(default=True, verbose_name='删除功能')
    allow_download = models.BooleanField(default=True, verbose_name='下载功能')
    allow_upload = models.BooleanField(default=True, verbose_name='上传功能')

    class Meta:
        verbose_name = '数据视图'
        unique_together = ('meta', 'code')


class MetaField(VModel):
    # 标识
    view = models.ForeignKey('MetaView', on_delete=models.CASCADE, verbose_name='数据视图')
    prop = models.CharField(max_length=100, verbose_name='字段名称')  #
    label = models.CharField(max_length=100, verbose_name='字段标签')  #
    name = models.CharField(max_length=100, verbose_name='字段别名')  #

    """tool"""
    domain = models.CharField(max_length=100, verbose_name='字段类型')  #
    tool = models.CharField(max_length=100, default='default', verbose_name='工具组件')
    refer = models.JSONField(default=dict, verbose_name='索引')  #
    format = models.JSONField(default=dict, verbose_name='格式')  #

    """rest"""
    disabled = models.BooleanField(default=False, verbose_name='禁用')  #
    not_null = models.BooleanField(default=False, verbose_name='不为空')  #
    allow_edit = models.BooleanField(default=True, verbose_name='可编辑')
    allow_order = models.BooleanField(default=True, verbose_name='可排序')
    allow_search = models.BooleanField(default=True, verbose_name='可搜索')
    allow_download = models.BooleanField(default=True, verbose_name='可下载')
    allow_upload = models.BooleanField(default=True, verbose_name='可上传')
    allow_update = models.BooleanField(default=True, verbose_name='可更新')

    """table"""
    unit = models.CharField(max_length=55, verbose_name='单位符', null=True)
    column_width = models.FloatField(default=0, verbose_name='表头宽度')
    align = models.CharField(max_length=55, null=True, verbose_name='对齐方式')  #
    fixed = models.CharField(max_length=100, verbose_name='固定位置', null=True)
    header_color = models.CharField(max_length=55, verbose_name='表头颜色', null=True)
    cell_color = models.CharField(max_length=55, verbose_name='单元颜色', null=True)
    edit_on_table = models.BooleanField(default=True, verbose_name='表格编辑')
    hide_on_table = models.BooleanField(default=False, verbose_name='表内隐藏')

    """form"""
    span = models.IntegerField(default=0, verbose_name='表单占位')
    hide_on_form = models.BooleanField(default=False, verbose_name='表单隐藏')
    hide_on_form_edit = models.BooleanField(default=False, verbose_name='编辑隐藏')
    hide_on_form_insert = models.BooleanField(default=False, verbose_name='新增隐藏')
    hide_on_form_branch = models.BooleanField(default=False, verbose_name='分支隐藏')
    hide_on_form_leaf = models.BooleanField(default=False, verbose_name='叶子隐藏')

    class Meta:
        verbose_name = '视图字段'
