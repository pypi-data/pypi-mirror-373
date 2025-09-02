from django.apps import apps
from django.db import connection
from django.db.models.signals import pre_migrate
from pytest_factoryboy import register
from wbcore.contrib.geography.tests.signals import app_pre_migration
from wbtasks.factories import TaskFactory

register(TaskFactory)


pre_migrate.connect(app_pre_migration, sender=apps.get_app_config("wbtasks"))
