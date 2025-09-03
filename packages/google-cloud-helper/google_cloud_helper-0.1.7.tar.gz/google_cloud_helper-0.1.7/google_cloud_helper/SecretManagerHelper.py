from google.cloud import secretmanager


class SecretManagerHelper:

    def __init__(self) -> None:
        """Initializes the SecretManagerHelper."""
        self.client = secretmanager.SecretManagerServiceClient()

    def get_secret(self, project_id: str, secret_id: str) -> str:
        """Retrieves a secret from Secret Manager.

        Args:
            project_id: The Google Cloud project ID.
            secret_id: The ID of the secret to retrieve.

        Returns:
            The secret value.
        """
        secret = self.client.access_secret_version(
            request={
                "name": f"projects/{project_id}/secrets/{secret_id}/versions/latest"
            }
        )
        return secret.payload.data.decode("UTF-8")
