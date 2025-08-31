meta_view_default_values = {
    'valar.Meta': {
        '__init__': {
            'allow_insert': False,
            'allow_upload': False,
            'lock': True
        }
    },
    'valar.MetaView': {
        '__init__': {
            'allow_insert': False,
            'allow_upload': False,
            'lock': True
        },
    },
    'valar.MetaField': {
        '__init__': {
            'allow_insert': False,
            'allow_upload': False,
            'lock': True
        },
        'tool': {
            'allow_edit_on_form': False,
        }
    }
}
