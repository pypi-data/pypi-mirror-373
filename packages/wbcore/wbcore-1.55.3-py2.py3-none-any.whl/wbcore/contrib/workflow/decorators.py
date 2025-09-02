from typing import Callable


def register(serializer_class=None):
    """
    Register the given model as a "workflowable" model
    """
    from wbcore.contrib.workflow.sites import workflow_site

    def _model_wrapper(model_class):
        workflow_site.registered_model_classes_serializer_map[model_class] = serializer_class
        return model_class

    return _model_wrapper


def register_assignee(name: str) -> Callable:
    from wbcore.contrib.workflow.sites import workflow_site

    def _wrapper(func: Callable) -> Callable:
        workflow_site.registered_assignees_methods[func.__name__] = func
        workflow_site.registered_assignees_names[func.__name__] = name
        return func

    return _wrapper
