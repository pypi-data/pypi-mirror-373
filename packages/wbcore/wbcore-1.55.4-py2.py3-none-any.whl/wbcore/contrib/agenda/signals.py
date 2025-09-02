from django.db.models.signals import ModelSignal

draggable_calendar_item_ids = (
    ModelSignal()
)  # Signal called to gather the list of calendar items that are considered draggable.
