from ..dao.abstract import AbstractField
from ..dao.frame import meta_field_tool_mapping


class MonField(AbstractField):

    def __init__(self, entity, prop, domain, tool):
        self.db = 'mon'
        self.entity = entity
        self.prop = prop
        self.label = prop
        self.domain = domain
        self.tool = tool

    def to_dict(self):
        _field = {
            "prop": self.prop,
            "label": self.label,
            "name": self.label,
            "domain": self.domain,
            'tool': self.tool,
        }
        return _field
