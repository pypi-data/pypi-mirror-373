from _typeshed import Incomplete
from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google_admin.services.base import GoogleAdminServiceBase as GoogleAdminServiceBase
from typing import Any

class GoogleAdminGroupsService(GoogleAdminServiceBase):
    """Service class for Google Admin groups operations.

    This class provides methods for interacting with the groups() endpoint
    of the Google Admin API.
    """
    version: str
    groups_service: Incomplete
    def __init__(self, credentials: GoogleCredentials) -> None:
        """Initialize the Google service with credentials.

        Args:
            credentials (GoogleCredentials): The credentials for the service
        """
    def list_groups(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get list of groups.

        Args:
            params: Parameters for the groups().list() request

        Returns:
            Dictionary containing the list of groups
        """
