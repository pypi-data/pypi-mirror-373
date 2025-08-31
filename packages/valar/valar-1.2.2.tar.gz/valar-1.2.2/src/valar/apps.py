import os
from django.apps import AppConfig
from valar_app_mixins.auto_migration_mixin import AutoMigrationMixin
from valar_app_mixins.auto_urlpatterns_mixin import AutoUrlPatternsMixin


class ValarConfig(AutoMigrationMixin, AutoUrlPatternsMixin, AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = __package__

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true':
            from .dao.frame import MetaFrame
            getattr(super(), 'set_url', None)()
            getattr(super(), 'auto_migrate', None)()
            MetaFrame()
