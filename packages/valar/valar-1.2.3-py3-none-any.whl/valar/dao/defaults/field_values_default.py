meta_field_value_defaults = {
    'valar.Meta': {
        "__init__": {
            "db": {
                "tool": "set",
                "format": {
                    "set": {
                        'orm': 'SQL',
                        'mon': 'MongoDB',
                        'center': '剧中对齐',
                    }
                }
            },
        }
    },
    'valar.MetaView': {
        "__init__": {
            "meta_id": {
                'allow_edit': False,
            },
            "code": {
                'allow_edit': False,
            },
            "name": {
                'span': 24
            }
        },
        "core": {
            "name": {
                'span': 16
            },
            "enable": {
                "span": 8
            }
        }
    },
    'valar.MetaFieldDomain': {
        "__init__": {
            "default_id": {
                "tool": "tree"
            },
            "search_id": {
                "tool": "tree"
            },
            "tools": {
                "tool": "tree",
                "refer": {
                    "display": "code"
                }
            },
            "align": {
                "tool": "set",
                "format": {
                    "set": {
                        'left': '左对齐',
                        'right': '右对齐',
                        'center': '剧中对齐',
                    }
                }
            }
        }
    },
    'valar.MetaField': {
        "rest": {
            "name": {
                'hide_on_form': False
            },
        },
        "__init__": {
            "column_width": {
                'unit': 'px'
            },
            "name": {
                'span': 24,
                'hide_on_form': True
            },
            "fixed": {
                "tool": "set",
                "format": {
                    "set": {
                        'left': '左侧固定',
                        'right': '右侧固定',
                    }
                }
            },
            "align": {
                "tool": "set",
                "format": {
                    "set": {
                        'left': '左对齐',
                        'right': '右对齐',
                        'center': '剧中对齐',
                    }
                }
            },
            "prop": {
                'allow_edit': False,
                'column_width': 120
            },
            "domain": {
                'allow_edit': False,
                'column_width': 120,
            },
            "tool": {
                'column_width': 100,
                'span': 24,
                'tool': 'tree',
                'refer': {
                    'entity': 'valar.MetaFieldTool',
                    'includes': {'metafielddomain__name': '${domain}'},
                    'value': 'code', 'display': 'code', "isTree": True
                }

            },
            "span": {
                'column_width': 100,
                "format": {"min": 0, "max": 24, "step": 1, "precision": 0, "step_strictly": True}
            },
            "refer": {
                'allow_edit': False,
                'column_width': 80
            },
            "format": {
                'allow_edit': False,
                'column_width': 80
            },
            'header_color': {
                'tool': 'color',
            },
            'cell_color': {
                'tool': 'color',
            }
        }
    }
}
