from wbcore.contrib.workflow.sites import workflow_site


def get_model_serializer_class_for_instance(instance):
    return workflow_site.registered_model_classes_serializer_map[instance.__class__]


def get_model_serializer_class_for_class(instance_class):
    return workflow_site.registered_model_classes_serializer_map[instance_class]


def model_is_registered_for_workflow(model) -> bool:
    return model in workflow_site.registered_model_classes_serializer_map.keys()
