import os
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.core import mail
from django.core.validators import URLValidator
from django.utils import timezone
from slugify import slugify
from wbcore.contrib.documents.models.documents import (
    Document,
    send_email_as_task,
    upload_to,
)


@pytest.mark.django_db
@pytest.mark.with_db
class TestDocumentModel:
    @pytest.fixture
    def email(self):
        return "foo@bar.com"

    def test_init(self, document):
        assert document.id is not None

    def test_upload_to(self, document, document_type_factory):
        parent_document_type = document_type_factory.create()
        document_type = document_type_factory.create(parent=parent_document_type)
        document.document_type = document_type
        document.save()
        assert (
            upload_to(document, "foo")
            == f"dms/document/{slugify(parent_document_type.name)}/{slugify(document_type.name)}/foo"
        )

    @pytest.mark.parametrize("document__file", ["/foo/bar"])
    def test_filename(self, document):
        assert document.filename == os.path.basename(document.file.name)

    def test_linked_objects(self, document_factory):
        document = document_factory.create()
        link_obj = document_factory.create()
        document.link(link_obj)
        assert list(document.linked_objects)[0] == link_obj

    @pytest.mark.parametrize(
        "sharing_seconds_duration, one_time_link",
        [(0, False), (1, False), (0, True), (1, True)],
    )
    def test_generate_shareable_link(self, document, sharing_seconds_duration, one_time_link):
        document.generate_shareable_link(
            sharing_seconds_duration=sharing_seconds_duration,
            one_time_link=one_time_link,
        )
        assert (
            document.shareable_links.filter(
                valid_until__isnull=sharing_seconds_duration == 0,
                one_time_link=one_time_link,
            ).count()
            == 1
        )

    @patch("wbcore.contrib.documents.models.documents.send_email_as_task.delay")
    def test_send_email(self, mock_fct, document, email):
        document.send_email(email)
        assert mock_fct.call_count == 1

    def test_get_for_object(self, document_factory):
        document = document_factory.create()
        link_obj = document_factory.create()
        document.link(link_obj)
        assert Document.get_for_object(link_obj).first() == document

    @pytest.mark.parametrize(
        "to_emails, as_link, subject, from_email, body",
        [
            (email, False, None, None, None),
            (email, False, "Some paragraph", email, "A different paragraph"),
            (email, True, None, None, None),
        ],
    )
    def test_send_email_as_task(self, document, to_emails, as_link, subject, from_email, body):
        assert len(mail.outbox) == 0
        send_email_as_task(
            document.id,
            to_emails,
            as_link=as_link,
            subject=subject,
            from_email=from_email,
            body=body,
        )
        assert len(mail.outbox) == 1
        msg = mail.outbox[0]
        if as_link:
            assert document.shareable_links.count() == 1
            assert len(msg.attachments) == 0
            assert len(msg.alternatives) == 1
        else:
            assert document.shareable_links.count() == 0
            assert len(msg.attachments) == 1
            assert len(msg.alternatives) == 2
        assert msg


@pytest.mark.django_db
class TestDocumentTypeModel:
    def test_init(self, document_type):
        assert document_type.id is not None

    def test_str(self, document_type_factory):
        document_type = document_type_factory.create(parent=document_type_factory.create())
        document_type.save()
        assert str(document_type) == document_type.compute_str()


@pytest.mark.django_db
class TestShareableLinkModel:
    @pytest.mark.parametrize(
        "shareable_link__manual_invalid, shareable_link__valid_until, shareable_link__one_time_link",
        [
            (True, None, False),
            (False, timezone.now() - timedelta(seconds=60), False),
            (False, None, True),
        ],
    )
    def test_unvalid_link(self, shareable_link):
        if shareable_link.one_time_link:
            assert shareable_link.is_valid()
            shareable_link.access()
        assert not shareable_link.is_valid()

    def test_link(self, shareable_link):
        URLValidator()(shareable_link.link)

    def test_access(self, shareable_link):
        assert shareable_link.accesses.count() == 0
        shareable_link.access()
        assert shareable_link.accesses.count() == 1

    def test_init(self, shareable_link):
        assert shareable_link.id is not None


@pytest.mark.django_db
class TestShareableLinkAccessModel:
    def test_init(self, shareable_link_access):
        assert shareable_link_access.id is not None
