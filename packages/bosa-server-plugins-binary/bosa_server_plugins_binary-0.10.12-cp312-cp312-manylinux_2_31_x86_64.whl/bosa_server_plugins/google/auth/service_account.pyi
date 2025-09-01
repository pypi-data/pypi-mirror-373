from _typeshed import Incomplete
from bosa_core import ConfigService as ConfigService
from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from google.oauth2.credentials import Credentials as Credentials

class ServiceAccountGoogleCredentials(GoogleCredentials):
    """Google authentication scheme using service account."""
    config: Incomplete
    scopes: Incomplete
    def __init__(self, config: ConfigService, scopes: list[str]) -> None:
        """Initialize Google Service Account authentication scheme.

        Args:
            config (ConfigService): The config service
            scopes (list[str]): The scopes
        """
    def get_credentials(self) -> Credentials:
        """Get the credentials.

        Returns:
            Credentials: The credentials
        """
