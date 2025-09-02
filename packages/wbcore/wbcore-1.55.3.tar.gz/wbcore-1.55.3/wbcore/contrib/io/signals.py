from django.db.models.signals import ModelSignal

# Signal fired after a import source was imported
post_import = ModelSignal(use_caching=False)
