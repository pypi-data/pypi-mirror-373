from django.db.models.signals import ModelSignal

# Signal fired before merged/obsolete object are deleted during a merge phase
post_clone = ModelSignal(use_caching=False)
