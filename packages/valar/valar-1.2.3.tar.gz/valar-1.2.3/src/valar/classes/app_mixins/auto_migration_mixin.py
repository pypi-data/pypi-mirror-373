from django.core.management import call_command

class AutoMigrationMixin:
    name = None  # 子类必须提供
    def auto_migrate(self):
        app = self.name.replace('src.', '')
        call_command('makemigrations', app, interactive=False, verbosity=0)
        call_command('migrate', app, interactive=False, verbosity=0)
