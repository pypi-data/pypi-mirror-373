import importlib

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from ..classes.singleton_meta import SingletonMeta

class ChannelMapping(metaclass=SingletonMeta):
    def __init__(self):
        mapping = settings.HANDLER_MAPPING
        root, name = mapping.rsplit('.', 1)
        module = importlib.import_module(root)
        if hasattr(module, name):
            self.mapping: dict = getattr(module, name)
        else:
            raise ImproperlyConfigured("%r has no attribute %r" % (root, name))

    def get_handler(self, handler):
        method = self.mapping.get(handler)
        if method is None:
            raise ImproperlyConfigured("Cannot find handler - %r" % handler)
        return method

