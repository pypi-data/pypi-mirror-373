import json
import logging
from io import BytesIO
from unittest.mock import patch

import pytest
from croniter import croniter
from django.core import files
from django.core.exceptions import ValidationError
from django.core.files.temp import NamedTemporaryFile
from django.db import IntegrityError
from django.utils import timezone
from django_celery_beat.models import cronexp
from faker import Faker
from pytest_factoryboy import LazyFixture

from ..backends.abstract import AbstractDataBackend
from ..models import (
    ImportCredential,
    ImportSource,
    ParserHandler,
    Source,
    generate_import_sources_as_task,
    import_data_as_task,
)
from ..utils import nest_row

logger = logging.getLogger("io")

fake = Faker()


def parse(data):
    return data


def test_nest_row():
    a = {
        "nest1__field1": "val1",
        "nest2__field2": "val2",
        "field3": "val3",
        "nest1__field4": "val4",
        "field4": "val5",
    }
    expected_res = {
        "nest1": {
            "field1": "val1",
            "field4": "val4",
        },
        "nest2": {"field2": "val2"},
        "field3": "val3",
        "field4": "val5",
    }
    assert nest_row(a) == expected_res


@pytest.mark.django_db
class TestParserHandlerModel:
    def test_init(self, parser_handler):
        assert parser_handler.id is not None

    def test_parse_module_not_found(self, parser_handler, import_source):
        with pytest.raises(ModuleNotFoundError):
            parser_handler.parse(import_source)

    def test_handle_lookup_error(self, parser_handler, import_source):
        with pytest.raises(LookupError):
            parser_handler.handle(import_source, dict(a="a"))

    @pytest.mark.parametrize("parser_handler__parser", ["wbcore.contrib.io.tests.test_models"])
    def test_parse(self, parser_handler):
        data = {"data": [dict(a=1, b="b")]}
        assert parser_handler.parse(data) == data


def get_test_file():
    image_temp_file = NamedTemporaryFile(delete=True, suffix=".csv")
    image_temp_file.write(json.dumps([{"a": "a", "b": "b"}]).encode())
    file_name = "temp.csv"  # Choose a unique name for the file
    image_temp_file.flush()
    return files.File(image_temp_file, name=file_name)


def get_byte_stream():
    data = {fake.name(): fake.name(), fake.name(): fake.name()}
    content_file = BytesIO()
    content_file.write(json.dumps(data).encode())
    return content_file


@pytest.mark.django_db
class TestSourceModel:
    def test_init(self, source):
        assert source.id is not None

    def test_crontab_repr(self, source):
        assert source.crontab_repr == "{0} {1} {2} {3} {4}".format(
            cronexp(source.crontab.minute),
            cronexp(source.crontab.hour),
            cronexp(source.crontab.day_of_month),
            cronexp(source.crontab.month_of_year),
            cronexp(source.crontab.day_of_week),
        )
        source.crontab = None
        source.save()

        assert source.crontab_repr == ""

    @pytest.mark.parametrize("source__crontab", [None, LazyFixture("crontab_schedule")])
    @pytest.mark.parametrize("_datetime", [fake.date_time()])
    def test_is_valid_date(self, source, _datetime):
        if not source.crontab:
            assert not source.is_valid_date(_datetime)
        else:
            assert source.is_valid_date(_datetime) == croniter.match(source.crontab_repr, _datetime)

    def test_process_source_without_backend(self, source_factory):
        with pytest.raises(IntegrityError):
            source_factory.create(data_backend=None)

    def test_process_source_void(self, source):
        assert ImportSource.objects.count() == 0
        source.generate_import_sources(timezone.now())
        assert ImportSource.objects.count() == 0

    @patch.object(AbstractDataBackend, "get_files")
    @pytest.mark.parametrize("data_backend__save_data_in_import_source", [True, False])
    def test_generate_import_sources(self, mock_get_files, data_backend, source_factory, parser_handler):
        source = source_factory.create(data_backend=data_backend)
        source.parser_handler.add(parser_handler)
        mock_get_files.return_value = [("test.csv", get_byte_stream())]
        assert ImportSource.objects.count() == 0
        list(source.generate_import_sources(timezone.now()))
        assert ImportSource.objects.count() == 1
        import_source = ImportSource.objects.first()
        if not import_source:
            raise ValueError("We expect an import source creation")
        assert import_source.source == source
        assert import_source.save_data == data_backend.save_data_in_import_source
        assert import_source.parser_handler == source.parser_handler.first()

    # def test_load_sources_from_setting(self, source_factory, parser_handler):
    #     source = source_factory.build()
    #     assert Source.objects.count() == 0
    #     settings = [
    #         (
    #             parser_handler.handler,
    #             parser_handler.parser,
    #             source.data_backend,
    #             {
    #                 "crontab": source.crontab_repr,
    #                 "import_parameters": source.import_parameters,
    #                 "connection_parameters": source.connection_parameters,
    #                 "is_active": source.is_active,
    #                 "credentials": [
    #                     {
    #                         "key": "test-credential",
    #                         "type": "CREDENTIAL",
    #                         "password": "password",
    #                         "username": "username",
    #                     }
    #                 ],
    #             },
    #         )
    #     ]
    #
    #     # Load source from settings, we expect one source creation
    #     assert ImportCredential.objects.count() == 0
    #     Source.load_sources_from_settings(settings)
    #     saved_source = Source.objects.first()
    #     assert saved_source.parser_handler.first().handler == parser_handler.handler
    #     assert saved_source.parser_handler.first().parser == parser_handler.parser
    #     assert saved_source.data_backend == source.data_backend
    #     assert saved_source.crontab_repr == source.crontab_repr
    #     assert saved_source.import_parameters == source.import_parameters
    #     assert saved_source.connection_parameters == source.connection_parameters
    #     assert saved_source.is_active == source.is_active
    #     assert saved_source.credentials.count() == 1
    #     assert saved_source.credentials.first() == ImportCredential.objects.first()
    #
    #     # Load source from settings, we shoudlnt't expect any creation
    #     Source.load_sources_from_settings(settings)
    #     assert Source.objects.count() == 1
    #     assert Source.objects.last() == saved_source

    @pytest.mark.parametrize("source__crontab", [None])
    def test_update_periodic_task_no_crontab(self, source):
        assert not source.periodic_task

    @pytest.mark.parametrize("source__is_active", [True, False])
    def test_update_periodic_task(self, source):
        source.update_periodic_task()
        assert source.periodic_task
        assert source.periodic_task.crontab == source.crontab
        assert source.is_active == source.periodic_task.enabled
        assert json.loads(source.periodic_task.args) == [source.id]


@pytest.mark.django_db
class TestImportSourceModel:
    def test_init(self, import_source):
        assert import_source.id is not None

    def test_parse_data_without_file(self, import_source):
        with pytest.raises(ValueError):
            import_source._parse_data()

    @patch.object(ParserHandler, "parse")
    @pytest.mark.parametrize("import_source__file", [get_test_file()])
    def test_parse_data(self, mock_parse, import_source):
        return_value = {"data": json.loads(import_source.file.read().decode("utf-8"))}
        mock_parse.return_value = return_value
        assert import_source._parse_data() == return_value
        assert mock_parse.call_count == 1

    @pytest.mark.parametrize("parser_handler__allow_file_type", [ParserHandler.MimeTypeChoices.CSV])
    def test_unvalidate_file_type(self, import_source_factory, parser_handler):
        with pytest.raises(ValidationError):
            unvalid_file = get_test_file()
            import_source_factory.create(file=unvalid_file, parser_handler=parser_handler)

    @pytest.mark.parametrize(
        "import_source__file,parser_handler__allow_file_type",
        [(get_test_file(), None), (None, ParserHandler.MimeTypeChoices.CSV)],
    )
    def test_unvalidate_file_type_but_nocheck(self, import_source, parser_handler):
        assert import_source

    @patch.object(ParserHandler, "handle")
    def test_process_data(self, mock_handle, import_source):
        def callback(_data):
            _data["a"] = "b"

        mock_handle.return_value = callback
        data = dict(data=[{"a": "a"}])
        import_source._process_data(data)
        assert mock_handle.call_count == 1
        assert data == {"data": [{"a": "a"}]}

    @patch.object(ParserHandler, "parse")
    @patch.object(ParserHandler, "handle")
    @pytest.mark.parametrize(
        "import_source__file, import_source__save_data",
        [(get_test_file(), True), (get_test_file(), False)],
    )
    def test_import_data_success(self, mock_handle, mock_parse, import_source):
        file_data = json.loads(import_source.file.read().decode("utf-8"))
        mock_parse.return_value = {"data": file_data}
        assert import_source.status == ImportSource.Status.PENDING
        import_source.import_data(debug=True)
        import_source.refresh_from_db()
        assert import_source.status == ImportSource.Status.PROCESSED
        assert mock_parse.call_count == 1
        assert mock_handle.call_count == 1
        if import_source.save_data:
            assert import_source.data == {"data": file_data}
        else:
            assert import_source.data == {}

    def test_import_data_error(self, caplog, import_source):
        assert import_source.status == ImportSource.Status.PENDING
        with caplog.at_level(logging.ERROR):
            import_source.import_data()
        assert import_source.status == ImportSource.Status.ERROR


@pytest.mark.django_db
class TestImportCredentialModel:
    def test_init(self, import_credential):
        assert import_credential.id is not None

    @pytest.mark.parametrize(
        "import_credential__validity_start, import_credential__validity_end",
        [(fake.date_time(), fake.date_time()), (None, None)],
    )
    def test_str(self, import_credential):
        assert str(import_credential)

    @pytest.mark.parametrize(
        "type, password, username, authentication_token,  certificate_pem, certificate_key",
        [
            (
                ImportCredential.Type.CREDENTIAL,
                None,
                "username",
                None,
                "certificate_pem",
                "certificate_key",
            ),
            (
                ImportCredential.Type.CREDENTIAL,
                "password",
                None,
                None,
                "certificate_pem",
                "certificate_key",
            ),
            (
                ImportCredential.Type.AUTHENTICATION_TOKEN,
                "password",
                "username",
                None,
                "certificate_pem",
                "certificate_key",
            ),
            (
                ImportCredential.Type.CERTIFICATE,
                "password",
                "username",
                "token",
                None,
                "certificate_key",
            ),
        ],
    )
    def test_unvalid_credential(
        self,
        import_credential_factory,
        type,
        password,
        username,
        authentication_token,
        certificate_pem,
        certificate_key,
    ):
        with pytest.raises(ValidationError):
            import_credential_factory.create(
                type=type,
                password=password,
                username=username,
                authentication_token=authentication_token,
                certificate_pem=certificate_pem,
                certificate_key=certificate_key,
            )

    @pytest.mark.parametrize(
        "type, username, password, authentication_token, certificate_pem, certificate_key",
        [
            (
                ImportCredential.Type.CREDENTIAL,
                None,
                None,
                fake.random_letters(16),
                None,
                None,
            ),
            (
                ImportCredential.Type.AUTHENTICATION_TOKEN,
                fake.random_letters(8),
                fake.random_letters(8),
                None,
                None,
                None,
            ),
            (
                ImportCredential.Type.CERTIFICATE,
                fake.random_letters(8),
                fake.random_letters(8),
                fake.random_letters(8),
                None,
                None,
            ),
        ],
    )
    def test_init_wrong_type(
        self,
        type,
        username,
        password,
        authentication_token,
        certificate_pem,
        certificate_key,
        import_credential_factory,
    ):
        with pytest.raises(ValidationError):
            import_credential_factory.create(
                type=type,
                username=username,
                password=password,
                authentication_token=authentication_token,
                certificate_pem=certificate_pem,
                certificate_key=certificate_key,
            )


@pytest.mark.django_db
class TestSharedTasks:
    @patch.object(ImportSource, "import_data")
    def test_import_data_as_task(self, mock_import_data, import_source):
        import_data_as_task(import_source.id)
        assert mock_import_data.call_count == 1

    @patch.object(Source, "generate_import_sources")
    def test_process_source_as_task(self, mock_process_source, source):
        generate_import_sources_as_task(source.id, timezone.now())
        assert mock_process_source.call_count == 1
