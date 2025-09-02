from rest_framework.reverse import reverse

from wbcore.metadata.configs.endpoints import EndpointViewConfig


class TransitionEndpointConfig(EndpointViewConfig):
    def get_create_endpoint(self, **kwargs) -> str:
        if step_id := self.view.kwargs.get("step_id"):
            return reverse("wbcore:workflow:transition-step-list", args=[step_id], request=self.request)
        if workflow_id := self.view.kwargs.get("workflow_id"):
            return reverse("wbcore:workflow:transition-workflow-list", args=[workflow_id], request=self.request)
        return super().get_create_endpoint(**kwargs)

    def get_instance_endpoint(self, **kwargs):
        if step_id := self.view.kwargs.get("step_id"):
            return reverse("wbcore:workflow:transition-step-list", args=[step_id], request=self.request)
        if workflow_id := self.view.kwargs.get("workflow_id"):
            return reverse("wbcore:workflow:transition-workflow-list", args=[workflow_id], request=self.request)
        return super().get_instance_endpoint(**kwargs)
