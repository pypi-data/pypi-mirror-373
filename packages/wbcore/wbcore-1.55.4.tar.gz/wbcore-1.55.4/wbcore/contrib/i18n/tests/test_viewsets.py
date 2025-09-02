from unittest.mock import MagicMock, patch

import pytest
from wbcore.contrib.i18n.viewsets import ModelTranslateMixin


class TestModel:
    """A simple test model for testing the ModelTranslateMixin."""

    id = 1


@pytest.fixture
def viewset():
    """Create a viewset instance for testing."""

    class TestViewSet(ModelTranslateMixin):
        def get_object(self):
            return TestModel()

    return TestViewSet()


@patch("wbcore.contrib.i18n.viewsets.translate_model_as_task")
@patch("wbcore.contrib.i18n.viewsets.ContentType.objects.get_for_model")
def test_auto_translate_success(mock_get_for_model, mock_translate_task, viewset, rf):
    """Test that auto_translate initiates a translation task and returns a success response."""
    # Setup
    mock_content_type = MagicMock()
    mock_content_type.id = 123
    mock_get_for_model.return_value = mock_content_type

    mock_translate_task.delay = MagicMock()

    request = rf.post("/auto-translate/")
    request.data = {}

    # Execute
    response = viewset.auto_translate(request)

    # Assert
    mock_get_for_model.assert_called_once()
    mock_translate_task.delay.assert_called_once_with(123, 1, False)

    assert response.status_code == 200
    assert response.data == {"__notification": "The translation started in the background."}


@patch("wbcore.contrib.i18n.viewsets.translate_model_as_task")
def test_auto_translate_no_object(mock_translate_task, viewset, rf):
    """Test that auto_translate returns an error response when no object is found."""
    # Setup
    viewset.get_object = MagicMock(return_value=None)
    mock_translate_task.delay = MagicMock()

    request = rf.post("/auto-translate/")
    request.data = {}
    # Execute
    response = viewset.auto_translate(request)

    # Assert
    mock_translate_task.delay.assert_not_called()

    # The viewset code uses status.HTTP_400_BAD_REQUEST
    assert response.status_code == 400
    assert "non_field_errors" in response.data
    assert response.data["non_field_errors"] == ["The URL was malformatted."]
