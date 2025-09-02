from wbcore.test.mixins import TestViewSet
from wbcore.test.utils import get_or_create_superuser


class TestPandasView(TestViewSet):
    def test_get_request(self):
        if self.factory is None:
            self._raise_warning_factory("test_get_request")
        else:
            obj, request, kwargs, _ = self._get_mixins_data()
            request.user = get_or_create_superuser()
            request.query_params = dict()
            request.parser_context = {}
            self.mvs.kwargs = kwargs
            response = self.mvs.as_view({"get": "list"})(request, **kwargs)
            assert response.status_code == 200
            assert "results" in response.data
            assert "aggregates" in response.data
            assert "messages" in response.data

    def execute_test(self):
        self.test_get_request()
