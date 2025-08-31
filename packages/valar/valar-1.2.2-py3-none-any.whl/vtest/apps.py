import os
from django.apps import AppConfig

from valar_app_mixins.auto_migration_mixin import AutoMigrationMixin

valar_app = __package__.replace('src.', '')


class VTestConfig(AutoMigrationMixin, AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = __package__

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true':
            from ..valar.dao.frame import MetaFrame
            getattr(super(), 'auto_migrate', None)()
            MetaFrame()
