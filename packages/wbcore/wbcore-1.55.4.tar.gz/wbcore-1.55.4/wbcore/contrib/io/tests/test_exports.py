from unittest.mock import patch

import pandas as pd
import pytest
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test.client import RequestFactory
from faker import Faker
from rest_framework.reverse import reverse
from rest_framework.test import force_authenticate

from ..enums import ExportFormat, get_django_import_export_format
from ..models import ExportSource, ParserHandler
from ..resources import ViewResource
from ..serializers import ParserHandlerModelSerializer
from ..viewsets import ParserHandlerModelViewSet
from .test_models import get_test_file

fake = Faker()


@pytest.mark.django_db
class TestExportSourceModel:
    def test_file_format(self, export_source):
        assert (
            export_source.file_format.CONTENT_TYPE
            == get_django_import_export_format(export_source.format).CONTENT_TYPE
        )

    def test_resource(self, export_source):
        r = export_source.resource
        assert isinstance(r, ViewResource)
        assert r.columns_map == export_source.resource_kwargs["columns_map"]
        assert r.serializer_class == ParserHandlerModelSerializer

    def test_empty_queryset(self, export_source):
        assert set(export_source.queryset) == set()

    def test_queryset(self, export_source_factory, parser_handler_factory):
        ph1 = parser_handler_factory.create()
        e1 = export_source_factory()
        assert set(e1.queryset) == {ph1}
        ph2 = parser_handler_factory.create()
        e2 = export_source_factory()

        assert set(e2.queryset) == {ph1, ph2}

    def test_queryset_with_filter(self, export_source_factory, parser_handler_factory):
        ph1 = parser_handler_factory.create()
        parser_handler_factory.create()  # noise

        # check with customer queryset and filtering
        query_str, query_params = ParserHandler.objects.filter(parser=ph1.parser).query.sql_with_params()
        export_source = export_source_factory.create(query_str=query_str, query_params=query_params)

        assert set(export_source.queryset) == {ph1}

    def test_get_export_filename(self, export_source):
        filename = export_source.get_export_filename()
        assert isinstance(filename, str)
        assert (
            export_source.file_format.get_extension() in filename
        )  # check that the filename is with the proper extension

    @patch("wbcore.contrib.io.models.send_notification")
    def test_notify(self, mock_fct, export_source):
        export_source.notify()
        assert mock_fct.call_count == 0  # 0 call count because there is neither no file nor status == processed

        export_source.status = ExportSource.Status.PROCESSED.value
        export_source.save()

        export_source.notify()
        assert mock_fct.call_count == 0  # Still need a file

        export_source.file = get_test_file()
        export_source.save()

        export_source.notify()
        assert mock_fct.call_count == 1  # Still need a file

    @patch.object(ExportSource, "notify")
    @pytest.mark.parametrize("export_source__format", [ExportFormat.CSV])
    def test_export_data(self, fct_mock, export_source, parser_handler):
        export_source.export_data()
        assert export_source.status == ExportSource.Status.PROCESSED.value
        with export_source.file.open() as file:
            df = pd.read_csv(file)
            assert df.loc[0, "id"] == parser_handler.id
            assert df.loc[0, "Parser"] == parser_handler.parser
            assert df.loc[0, "Handler"] == parser_handler.handler
        assert fct_mock.call_count == 1

    # INFO This test is obsolete
    # def test_view_export_under_pagination_limit(self, superuser, parser_handler_factory):
    #     parser_handler_factory.create()
    #
    #     url = reverse("wbcore:io:parserhandler-processexport", args=[])
    #     request = RequestFactory().get(url, {"export_format": 0})
    #     force_authenticate(request, user=superuser)
    #     view = ParserHandlerModelViewSet.as_view({"get": "process_export"})
    #     response = view(request)
    #     assert response.headers["Content-Type"] == "text/csv"

    def test_view_export_over_pagination_limit(self, superuser, parser_handler_factory):
        assert ExportSource.objects.count() == 0

        settings.WBIMPORT_EXPORT_DEFAULT_EXPORT_PAGINATION_LIMIT = 1

        parser_handler_factory.create()

        url = reverse("wbcore:io:parserhandler-processexport", args=[])
        request = RequestFactory().patch(url, {"format": 0}, content_type="application/json")
        request.query_params = {}

        force_authenticate(request, user=superuser)
        view = ParserHandlerModelViewSet.as_view({"patch": "process_export"})
        response = view(request)
        assert response.status_code == 200

        _view = ParserHandlerModelViewSet()
        _view.request = request
        query_str, query_params = _view.filter_queryset(_view.get_queryset()).query.sql_with_params()
        assert ExportSource.objects.get(
            creator=superuser,
            content_type=ContentType.objects.get_for_model(ParserHandler),
            resource_path="wbcore.contrib.io.resources.ViewResource",
            query_str=query_str,
            query_params=query_params,
        )
