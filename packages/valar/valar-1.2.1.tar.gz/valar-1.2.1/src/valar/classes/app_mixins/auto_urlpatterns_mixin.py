import importlib

from django.conf import settings
from django.urls import path, include


class AutoUrlPatternsMixin:
    name = None  # 子类必须提供

    def set_url(self):
        root = settings.ROOT_URLCONF
        module = importlib.import_module(root)
        urlpatterns: list = getattr(module, 'urlpatterns')
        url = f'{self.name}.urls'
        urlpatterns.append(path('valar/', include(url)))
