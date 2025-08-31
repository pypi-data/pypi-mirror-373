import os
from django.apps import AppConfig
from .classes.app_mixins.auto_migration_mixin import AutoMigrationMixin
from .classes.app_mixins.auto_urlpatterns_mixin import AutoUrlPatternsMixin

valar_app = __package__.replace('src.', '')


class ValarConfig(AutoMigrationMixin, AutoUrlPatternsMixin, AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = __package__

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true':
            from .dao.frame import MetaFrame
            getattr(super(), 'set_url', None)()
            getattr(super(), 'auto_migrate', None)()
            MetaFrame()
