from _typeshed import Incomplete
from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google.services.base import GoogleServiceBase as GoogleServiceBase
from typing import Any

class GoogleUserInfoService(GoogleServiceBase):
    """Service class for Google OAuth2 API."""
    name: str
    version: str
    userinfo_service: Incomplete
    def __init__(self, credentials: GoogleCredentials) -> None:
        """Initialize the Google service with credentials.

        Args:
            credentials (GoogleCredentials): The credentials for the service
        """
    def get_user_info(self) -> dict[str, Any]:
        """Get user information from Google OAuth2 API.

        Returns:
            Dict[str, Any]: User information
        """
