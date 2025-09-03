from unittest import mock

import pytest
from google.api_core import exceptions

from google_cloud_helper.GoogleBucketHelper import GoogleBucketHelper


@pytest.fixture
def mock_storage_client():
    """Mocks the storage.Client."""
    with mock.patch(
        "google_cloud_helper.GoogleBucketHelper.storage.Client"
    ) as mock_client:
        yield mock_client


def test_download_as_text_success(mock_storage_client):
    """Tests that download_as_text successfully retrieves a file as a string."""
    # Arrange
    mock_client_instance = mock_storage_client.return_value
    mock_bucket = mock.Mock()
    mock_blob = mock.Mock()
    mock_blob.download_as_text.return_value = "file content"

    mock_client_instance.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    helper = GoogleBucketHelper(project_id="test-project")
    bucket_name = "test-bucket"
    file_path = "path/to/file.txt"

    # Act
    content = helper.download_as_text(bucket_name, file_path)

    # Assert
    mock_client_instance.bucket.assert_called_once_with(bucket_name)
    mock_bucket.blob.assert_called_once_with(file_path)
    mock_blob.download_as_text.assert_called_once()
    assert content == "file content"


def test_exists_bucket_true(mock_storage_client):
    """Tests that bucket_exists returns True when the bucket is found."""
    # Arrange
    mock_client_instance = mock_storage_client.return_value
    helper = GoogleBucketHelper(project_id="test-project")
    bucket_name = "existing-bucket"

    # Act
    exists = helper.exists_bucket(bucket_name)

    # Assert
    mock_client_instance.get_bucket.assert_called_once_with(bucket_name)
    assert exists is True


def test_exists_bucket_false(mock_storage_client):
    """Tests that bucket_exists returns False when the bucket is not found."""
    # Arrange
    mock_client_instance = mock_storage_client.return_value
    mock_client_instance.get_bucket.side_effect = exceptions.NotFound(
        "Bucket not found"
    )
    helper = GoogleBucketHelper(project_id="test-project")
    bucket_name = "non-existent-bucket"

    # Act
    exists = helper.exists_bucket(bucket_name)

    # Assert
    mock_client_instance.get_bucket.assert_called_once_with(bucket_name)
    assert exists is False
