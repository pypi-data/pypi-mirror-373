from django.dispatch import Signal

add_additional_resource = Signal()  # "serializer", "instance", "request", "user"
add_instance_additional_resource = Signal()  # "serializer", "instance", "request", "user"
add_dynamic_button = Signal()  # "serializer", "instance", "request", "user"
