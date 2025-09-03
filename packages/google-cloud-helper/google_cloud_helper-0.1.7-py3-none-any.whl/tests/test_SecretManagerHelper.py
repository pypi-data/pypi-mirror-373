from unittest import mock

import pytest
from google.api_core import exceptions

from google_cloud_helper.SecretManagerHelper import SecretManagerHelper


@pytest.fixture
def mock_secret_manager_client():
    """Mocks the SecretManagerServiceClient."""
    with mock.patch(
        "google_cloud_helper.SecretManagerHelper.secretmanager.SecretManagerServiceClient"
    ) as mock_client:
        yield mock_client


def test_get_secret_success(mock_secret_manager_client):
    """
    Tests that get_secret successfully retrieves and decodes a secret.
    """
    # Arrange
    mock_client_instance = mock_secret_manager_client.return_value
    mock_secret_payload = mock.Mock()
    mock_secret_payload.payload.data = b"my-super-secret-value"
    mock_client_instance.access_secret_version.return_value = mock_secret_payload

    helper = SecretManagerHelper()
    project_id = "test-project"
    secret_id = "test-secret"

    # Act
    secret_value = helper.get_secret(project_id, secret_id)

    # Assert
    expected_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    mock_client_instance.access_secret_version.assert_called_once_with(
        request={"name": expected_name}
    )
    assert secret_value == "my-super-secret-value"


def test_get_secret_not_found(mock_secret_manager_client):
    """Tests that an exception is raised if the secret is not found."""
    mock_client_instance = mock_secret_manager_client.return_value
    mock_client_instance.access_secret_version.side_effect = exceptions.NotFound(
        "Secret not found"
    )
    helper = SecretManagerHelper()
    with pytest.raises(exceptions.NotFound):
        helper.get_secret("test-project", "non-existent-secret")
