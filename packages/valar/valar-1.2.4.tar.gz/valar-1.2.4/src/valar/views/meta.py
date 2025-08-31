import json

from django.db.models import Count, Q

from ..classes.valar_response import ValarResponse
from ..dao import Dao
from ..dao.abstract import AbstractField

from ..dao.meta import ValarMeta
from ..models.meta import MetaView, Meta, MetaField


def upload_mapping(request):
    body = json.loads(request.body)
    db = body.get('db')
    entity = body.get('entity')
    code = body.get('code')
    fields = MetaField.objects.filter(
        view__meta__db=db,
        view__meta__entity=entity,
        view__code=code,
        domain__in=['ManyToManyField', 'ManyToManyRel', 'ManyToOneRel', 'OneToOneField', 'OneToOneRel', 'ForeignKey']
    ).filter(Q(allow_upload=True) | Q(allow_update=True))
    mapping = {}
    for field in fields:
        prop = field.prop
        refer = field.refer
        db = refer['db']
        entity = refer['entity']
        value = refer['value']
        label = refer['label']
        includes = {prop: refer['includes'][prop] for prop in refer['includes'] if not prop.startswith('$')}
        excludes = {prop: refer['excludes'][prop] for prop in refer['excludes'] if not prop.startswith('$')}
        values = Dao(entity, db).manager.filter(**includes).exclude(**excludes).values(*[value, label])
        mapping[prop] = {
            row[value]: row[label]
            for row in values if row[value]
        }
    return ValarResponse(mapping)


def meta_view(request, db, entity):
    body = json.loads(request.body)
    code = body.get('code')
    meta = ValarMeta(db, entity, code)
    _view = meta.meta_view()
    return ValarResponse(_view)


def load_customs(request):
    body = json.loads(request.body)
    db = body.get('db')
    entity = body.get('entity')
    code = body.get('code')
    ps = MetaField.objects.filter(
        view__code=code, view__meta__db=db, view__meta__entity=entity,
        domain='Custom').values('prop')
    current = [p.get('prop') for p in ps]
    return ValarResponse(current)


def get_fields(request):
    body = json.loads(request.body)
    db = body.get('db')
    entity = body.get('entity')
    route = body.get('route')
    dao = Dao(entity, db)
    array = []
    for prop in dao.fields:
        field: AbstractField = dao.fields.get(prop)
        if field is None:
            continue
        domain: str = field.domain
        if domain is None or domain.startswith('ManyTo'):
            continue
        elif domain in ['ForeignKey', 'OneToOneRel', 'OneToOneField']:
            refer = field.refer or {}
            _db = refer.get('db')
            _entity = refer.get('entity')
            _dao = Dao(_entity, _db)
            if f'{_db}.{_entity}' in route:
                continue
            array.append({
                'label': field.label,
                'value': field.prop.replace('_id', ''),
                'isLeaf': False,
                'db': _db,
                'entity': _entity,
            })
        elif len(route) > 1:
            array.append({
                'label': field.label,
                'value': field.prop,
                'isLeaf': True,
            })
    return ValarResponse(array)


def save_custom(request):
    return ValarResponse(True)


def add_fields(request):
    body = json.loads(request.body)
    view_id = body.get('view_id')
    props = body.get('props')
    view_dao = Dao('valar.MetaView')
    field_dao = Dao('valar.MetaField')
    view: MetaView = view_dao.find_one(view_id)
    entity = view.meta.entity
    db = view.meta.db
    dao = Dao(entity, db)
    for prop in props:
        field: AbstractField = dao.fields.get(prop)
        if field:
            _field = field.to_dict()
            _field['view_id'] = view_id
            field_dao.save_one(_field)

    return ValarResponse(True)


def metas(request):
    values = Meta.objects.all().values('db', 'entity', 'name', 'tree', 'metaview__name')
    mapping = {'orm': {'valar': []}, 'mon': []}
    for row in values:
        db = row['db']
        label = row['name']
        value = row['entity']
        tree = row['tree']
        icon = 'folder-tree' if tree else 'table'
        row.update({'label': label, 'value': value, 'icon': icon})
        if db == 'orm':
            app, _ = value.split('.')
            array = mapping['orm'].get(app, [])
            array.append(row)
            mapping['orm'][app] = array
        elif db == 'mon':
            mapping['mon'].append(row)

    mon = {'label': 'MongoDB', 'value': 'mon', 'icon': 'boxes', 'children': mapping['mon']}
    orm = {
        'label': 'SQL', 'value': 'orm', 'icon': 'boxes',
        'children': [
            {'label': app, 'value': app, 'icon': 'box', 'children': mapping['orm'][app]}
            for app in mapping['orm']
        ]
    }

    return ValarResponse([orm, mon])
