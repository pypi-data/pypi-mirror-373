from django.db import connection


def app_pre_migration(sender, app_config, **kwargs):
    cur = connection.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    cur.execute("CREATE EXTENSION IF NOT EXISTS btree_gin;")
