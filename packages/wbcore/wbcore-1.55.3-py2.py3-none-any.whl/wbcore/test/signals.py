from django.dispatch import Signal

get_custom_factory = Signal()
custom_update_data_from_factory = Signal()
custom_update_kwargs = Signal()
get_custom_serializer = Signal()
