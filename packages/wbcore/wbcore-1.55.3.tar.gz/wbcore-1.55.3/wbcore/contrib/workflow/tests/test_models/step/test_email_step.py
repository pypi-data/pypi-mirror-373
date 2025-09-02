import pytest
from django.conf import settings
from django.template import TemplateSyntaxError
from pytest_mock import MockerFixture
from wbcore.contrib.workflow.models import EmailStep, ProcessStep


class TestEmailStep:
    @pytest.fixture
    def mocked_email_step(self, mocker: MockerFixture):
        mocked_email_step = mocker.MagicMock(spec=EmailStep)
        mocked_email_step.subject = "Test Subject"
        mocked_email_step.template.file = "<html>Email content</html>"
        mocked_email_step.to.values_list.return_value = ["to@example.com"]
        mocked_email_step.cc.values_list.return_value = [
            "cc1@example.com",
            "cc2@example.com",
        ]
        mocked_email_step.bcc.values_list.return_value = []
        return mocked_email_step

    @pytest.fixture
    def mocked_process_step(self, mocker: MockerFixture):
        mocked_process_step = mocker.MagicMock(spec=ProcessStep)
        mocked_process_step.get_endpoint_basename.return_value = "process-step"
        mocked_process_step.id = 123
        return mocked_process_step

    @pytest.fixture(autouse=True)
    def patching(self, mocker: MockerFixture):
        mocker.patch(
            "wbcore.contrib.workflow.models.step.base_domain",
            return_value="https://testserver.com",
        )
        mocker.patch(
            "wbcore.contrib.workflow.models.step.reverse",
            return_value="/api/process-step/123/",
        )

    def test_run(self, mocker: MockerFixture, mocked_process_step, mocked_email_step):
        # Arrange
        mocked_template_render = mocker.patch(
            "django.template.Template.render",
            return_value="<html>Rendered content</html>",
        )
        mocked_email_init = mocker.patch("django.core.mail.EmailMultiAlternatives.__init__", return_value=None)
        mocked_email_send = mocker.patch("django.core.mail.EmailMultiAlternatives.send")
        mocked_attach_alternative = mocker.patch("django.core.mail.EmailMultiAlternatives.attach_alternative")
        mocker.patch(
            "wbcore.contrib.workflow.models.step.convert_html2text",
            return_value="Rendered content",
        )
        mocked_execute_single_next_step = mocker.patch.object(mocked_email_step, "execute_single_next_step")
        # Act
        EmailStep.run(mocked_email_step, mocked_process_step)
        # Assert
        mocked_template_render.assert_called_once_with(mocker.ANY)
        mocked_email_init.assert_called_once_with(
            "Test Subject",
            "Rendered content",
            settings.DEFAULT_FROM_EMAIL,
            to=["to@example.com"],
            cc=["cc1@example.com", "cc2@example.com"],
            bcc=[],
        )
        mocked_attach_alternative.assert_called_once_with("<html>Rendered content</html>", "text/html")
        mocked_email_send.assert_called_once()
        mocked_execute_single_next_step.assert_called_once_with(mocked_process_step)

    def test_run_failed(self, mocker: MockerFixture, mocked_process_step, mocked_email_step):
        # Arrange
        mocked_template_render = mocker.patch(
            "django.template.Template.render",
            side_effect=TemplateSyntaxError("Invalid syntax"),
        )
        mocked_email_send = mocker.patch("django.core.mail.EmailMultiAlternatives.send")
        mocked_execute_single_next_step = mocker.patch.object(mocked_email_step, "execute_single_next_step")
        mocked_set_failed = mocker.patch.object(mocked_email_step, "set_failed")
        # Act
        EmailStep.run(mocked_email_step, mocked_process_step)
        # Assert
        mocked_template_render.assert_called_once_with(mocker.ANY)
        mocked_email_send.assert_not_called()
        mocked_execute_single_next_step.assert_not_called()
        mocked_set_failed.assert_called_once_with(mocked_process_step, "Error in template syntax!")
