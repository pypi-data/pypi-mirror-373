from django.db import connection
from django.db.models.signals import pre_migrate
from pytest_factoryboy import register

from .test.factories import EntityTestFactory


def app_pre_migration(sender, app_config, **kwargs):
    cur = connection.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    cur.execute("CREATE EXTENSION IF NOT EXISTS btree_gin;")
    cur.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")


pre_migrate.connect(app_pre_migration)
register(EntityTestFactory)
register(
    EntityTestFactory,
    "entity_test_over_1000",
    dl_parameters={
        "data": {
            "path": "wbcore.contrib.dataloader.tests.test.dataloaders.dataloaders.RandomDataOver1000",
            "parameters": {},
        }
    },
)
