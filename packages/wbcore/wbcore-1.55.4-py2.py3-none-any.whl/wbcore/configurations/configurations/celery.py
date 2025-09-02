from configurations import values


class CeleryTest:
    CELERY_TASK_ALWAYS_EAGER = True


class Celery:
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        "max_retries": 3,
        "interval_start": 0,
        "interval_step": 0.2,
        "interval_max": 0.5,
    }
    CELERY_BROKER_URL = values.Value("redis://localhost:6379", environ_name="REDIS_URL", environ_prefix=None)
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = values.BooleanValue(True, environ_prefix=None)
    CELERY_TASK_SERIALIZER = values.Value("pickle", environ_prefix=None)
    CELERY_ACCEPT_CONTENT = values.ListValue(["json", "pickle"], environ_prefix=None)
    CELERY_RESULT_SERIALIZER = values.Value("pickle", environ_prefix=None)
    CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
    CELERY_RESULT_BACKEND = values.Value("redis://localhost:6379", environ_name="REDIS_URL", environ_prefix=None)

    if "rediss://" in CELERY_BROKER_URL:
        CELERY_BROKER_USE_SSL = {"ssl_cert_reqs": "none"}
    else:
        CELERY_BROKER_USE_SSL = {}
