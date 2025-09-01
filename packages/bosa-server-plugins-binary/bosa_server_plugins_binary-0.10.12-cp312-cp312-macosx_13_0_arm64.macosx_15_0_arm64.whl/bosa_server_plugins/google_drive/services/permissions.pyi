from _typeshed import Incomplete
from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google_drive.services.base import GoogleDriveServiceBase as GoogleDriveServiceBase
from typing import Any

class GoogleDrivePermissionsService(GoogleDriveServiceBase):
    """Service class for Google Drive permission operations.

    This class provides methods for interacting with the permissions() endpoint
    of the Google Drive API.
    """
    permissions_service: Incomplete
    def __init__(self, credentials: GoogleCredentials) -> None:
        """Initialize the Google service with credentials.

        Args:
            credentials (GoogleCredentials): The credentials for the service
        """
    def get_permission(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get permission details.

        Args:
            params: Parameters for the permissions().get() request

        Returns:
            The permission details
        """
    def list_permissions(self, params: dict[str, Any]) -> dict[str, Any]:
        """List permissions.

        Args:
            params: Parameters for the permissions().list() request

        Returns:
            List of permissions
        """
    def create_permission(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a permission.

        Args:
            params: Parameters for the permissions().create() request

        Returns:
            The created permission's metadata
        """
    def update_permission(self, params: dict[str, Any]) -> dict[str, Any]:
        """Update a permission.

        Args:
            params: Parameters for the permissions().update() request

        Returns:
            The updated permission's metadata
        """
    def delete_permission(self, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a permission.

        Args:
            params: Parameters for the permissions().delete() request

        Returns:
            Empty response upon success
        """
