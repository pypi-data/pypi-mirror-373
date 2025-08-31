meta_field_key_defaults = {
    'valar.Meta': {
        'default': ('pick', ['db', 'entity', 'name', 'tree']),
    },
    'valar.MetaView': {
        'list': ('pick', ['code', 'name']),
        'core': ('pick', ['name', 'enable', 'lock', 'property']),
        'style': ('pick', ['form_width', 'form_height', 'table_width', 'table_height']),
        'rest': ('pick',
                 ['allow_search', 'allow_order', 'allow_insert', 'allow_remove', 'allow_download', 'allow_upload']),
        'edit': ('pick', ['allow_edit', 'allow_edit_on_form', 'allow_edit_on_cell', 'allow_edit_on_sort']),
    },
    'valar.MetaField': {
        'tool': (
            'pick',
            [
                'name', 'domain', 'tool', 'refer', 'format'
            ]
        ),
        'rest': (
            'pick',
            [
                'name', 'not_null',
                'allow_edit', 'allow_sort', 'allow_search', 'allow_download', 'allow_upload', 'allow_update'
            ]
        ),
        'table': (
            'pick',
            [
                'name', 'unit', 'column_width', 'fixed', 'align', 'edit_on_table', 'hide_on_table',
                'header_color', 'cell_color'
            ]
        ),
        'form': (
            'pick',
            [
                'name', 'span',
                'hide_on_form', 'hide_on_form_insert', 'hide_on_form_edit', 'hide_on_form_branch', 'hide_on_form_leaf'
            ]
        ),
    },
    'valar.Valar': {
        'simple': ('pick', ['id', 'name', 'text_field', 'boolean_field', 'integer_field', 'float_field']),
        'date': ('pick', ['id', 'name', 'date_field', 'datetime_field', 'time_field']),
        'special': ('pick', ['id', 'name', 'text_field', 'json_field', 'file', 'm2m']),
        'ref': ('pick', ['id', 'name', 'm2o', 'm2m', 'o2o_id']),
    },
}
