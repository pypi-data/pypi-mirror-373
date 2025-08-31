import copy

from ..classes.singleton_meta import SingletonMeta


class MetaFrame(metaclass=SingletonMeta):
    def __init__(self):
        from .orm_dao import OrmDao
        from .meta import ValarMeta
        from ..models.core import VTree
        from .engine import ValarEngine
        tool_dao = OrmDao('valar.MetaFieldTool')
        domain_dao = OrmDao('valar.MetaFieldDomain')
        tool_dao.delete()
        domain_dao.delete()
        mapping = {}
        for item in meta_field_tool:
            item = copy.deepcopy(item)
            _id, code = item['id'], item['code']
            item.update({"saved": True})
            if item['isLeaf']:
                mapping[code] = _id
            tool_dao.save_one(item, True)
        for row in meta_field_domain:
            row = copy.deepcopy(row)
            default_id, tools = row['default_id'], row['tools']
            _row = copy.deepcopy(row)
            _row.update({
                'default_id': mapping[default_id],
                'tools': [mapping[tool] for tool in tools],
                "saved": True
            })
            domain_dao.save_one(_row)

        meta_dao = OrmDao('valar.Meta')
        meta_dao.delete([{"includes": {'db__exact': 'orm', 'entity__startswith': 'valar.'}}])
        engine = ValarEngine()
        for entity, model in engine.orm_engine.items():
            tree = issubclass(model, VTree)
            ValarMeta('orm', entity, 'default')
        cols = engine.mongo_engine.list_collections()
        for col in cols:
            entity = col['name']
            ValarMeta('mon', entity, 'default')


meta_field_tool = [
    {'id': 2, 'sort': 32, 'pid': 7, 'isLeaf': True, 'name': '输入框', 'code': 'text', 'align': 'left'},
    {'id': 3, 'sort': 17, 'pid': 0, 'isLeaf': False, 'name': 'SPEC', 'code': '特殊工具集'},
    {'id': 5, 'sort': 22, 'pid': 0, 'isLeaf': False, 'name': 'DATE', 'code': '日期时间工具集'},
    {'id': 6, 'sort': 21, 'pid': 8, 'isLeaf': True, 'name': '数字输入', 'code': 'number', 'align': 'right'},
    {'id': 7, 'sort': 36, 'pid': 0, 'isLeaf': False, 'name': 'TEXT', 'code': '文本工具集'},
    {'id': 8, 'sort': 26, 'pid': 0, 'isLeaf': False, 'name': 'NUMB', 'code': '数字工具集'},
    {'id': 9, 'sort': 10, 'pid': 0, 'isLeaf': False, 'name': 'FILE', 'code': '文件工具集'},
    {'id': 10, 'sort': 27, 'pid': 0, 'isLeaf': False, 'name': 'BOOL', 'code': '逻辑工具集'},
    {'id': 11, 'sort': 31, 'pid': 0, 'isLeaf': False, 'name': 'LIST', 'code': '列表工具集'},
    {'id': 12, 'sort': 8, 'pid': 3, 'isLeaf': True, 'name': '对象', 'code': 'object', 'align': 'center'},
    {'id': 13, 'sort': 5, 'pid': 9, 'isLeaf': True, 'name': '图片上传', 'code': 'image', 'align': 'center'},
    {'id': 14, 'sort': 2, 'pid': 9, 'isLeaf': True, 'name': '文件上传', 'code': 'file', 'align': 'center'},
    {'id': 15, 'sort': 13, 'pid': 7, 'isLeaf': True, 'name': '富文本', 'code': 'rich', 'align': 'center'},
    {'id': 17, 'sort': 11, 'pid': 10, 'isLeaf': True, 'name': '开关', 'code': 'switch', 'align': 'center'},
    {'id': 19, 'sort': 9, 'pid': 7, 'isLeaf': True, 'name': '颜色选择', 'code': 'color', 'align': 'center'},
    {'id': 20, 'sort': 14, 'pid': 11, 'isLeaf': True, 'name': '穿梭框', 'code': 'transfer', 'align': 'left'},
    {'id': 21, 'sort': 16, 'pid': 7, 'isLeaf': True, 'name': '自动填充', 'code': 'auto', 'align': 'left'},
    {'id': 22, 'sort': 35, 'pid': 5, 'isLeaf': True, 'name': '日期选择', 'code': 'date', 'align': 'left'},
    {'id': 23, 'sort': 12, 'pid': 10, 'isLeaf': True, 'name': '逻辑选择', 'code': 'boolean', 'align': 'center'},
    {'id': 24, 'sort': 24, 'pid': 11, 'isLeaf': True, 'name': '列表选择', 'code': 'select', 'align': 'left'},
    {'id': 25, 'sort': 15, 'pid': 11, 'isLeaf': True, 'name': '树形选择', 'code': 'tree', 'align': 'left'},
    {'id': 26, 'sort': 23, 'pid': 11, 'isLeaf': True, 'name': '及联选择', 'code': 'cascade', 'align': 'left'},
    {'id': 28, 'sort': 25, 'pid': 7, 'isLeaf': True, 'name': '图标', 'code': 'icon', 'align': 'center'},
    {'id': 32, 'sort': 30, 'pid': 7, 'isLeaf': True, 'name': '文本框', 'code': 'textarea', 'align': 'left'},
    {'id': 33, 'sort': 18, 'pid': 36, 'isLeaf': True, 'name': '时间区间', 'code': 'timerange', 'align': 'left'},
    {'id': 35, 'sort': 33, 'pid': 5, 'isLeaf': True, 'name': '时间选择', 'code': 'time', 'align': 'left'},
    {'id': 36, 'sort': 20, 'pid': 0, 'isLeaf': False, 'name': 'RANGE', 'code': '区间工具集'},
    {'id': 37, 'sort': 38, 'pid': 36, 'isLeaf': True, 'name': '日期区间', 'code': 'daterange', 'align': 'left'},
    {'id': 39, 'sort': 3, 'pid': 36, 'isLeaf': True, 'name': '多日期', 'code': 'dates', 'align': 'left'},
    {'id': 54, 'sort': 54, 'pid': 7, 'isLeaf': True, 'name': '集合', 'code': 'set', 'align': 'left'},
    {'id': 31, 'sort': 6, 'pid': 0, 'isLeaf': True, 'name': '无', 'code': 'none', 'align': 'left'},
]

meta_field_tool_mapping = {
    row['code']: row['align']
    for row in meta_field_tool
    if row['isLeaf']
}
meta_field_domain = [
    {
        'name': 'CharField',
        'default_id': 'text',
        'tools': [
            'text', 'number', 'color', 'auto', 'date', 'time', 'select', 'tree', 'cascade', 'icon',
            'textarea', 'timerange', 'daterange', 'dates', 'set'
        ]
    },
    {
        'name': 'TextField',
        'default_id': 'textarea',
        'tools': ['text', 'textarea', 'rich']
    },
    {
        'name': 'BooleanField',
        'default_id': 'switch',
        'tools': ['switch', 'boolean']
    },
    {
        'name': 'IntegerField',
        'default_id': 'number',
        'tools': ['number']
    },
    {
        'name': 'FloatField',
        'default_id': 'number',
        'tools': ['number']
    },
    {
        'name': 'ForeignKey',
        'default_id': 'select',
        'tools': ['select', 'tree', 'cascade']
    },
    {
        'name': 'ManyToOneRel',
        'default_id': 'select',
        'tools': ['transfer', 'select', 'tree', 'cascade']
    },
    {
        'name': 'ManyToManyField',
        'default_id': 'select',
        'tools': ['transfer', 'select', 'tree', 'cascade']
    },
    {
        'name': 'ManyToManyRel',
        'default_id': 'select',
        'tools': ['transfer', 'select', 'tree', 'cascade']
    },
    {
        'name': 'OneToOneRel',
        'default_id': 'select',
        'tools': ['select']
    },
    {
        'name': 'OneToOneField',
        'default_id': 'select',
        'tools': ['select']
    },
    {
        'name': 'DateField',
        'default_id': 'date',
        'tools': ['date']
    },
    {
        'name': 'TimeField',
        'default_id': 'time',
        'tools': ['time']
    },
    {
        'name': 'DateTimeField',
        'default_id': 'date',
        'tools': ['date']
    },
    {
        'name': 'JSONField',
        'default_id': 'object',
        'tools': ['object']
    },
    {
        'name': 'FileField',
        'default_id': 'file',
        'tools': ['image', 'file']
    },
    {
        'name': 'BigAutoField',
        'default_id': 'none',
        'tools': ['none']
    },
    {
        'name': 'UUIDField',
        'default_id': 'none',
        'tools': ['none']
    },
    {
        'name': 'Custom',
        'default_id': 'none',
        'tools': ['none']
    },
]
meta_field_domain_mapping = {
    row['name']: row['default_id']
    for row in meta_field_domain
}
