from _typeshed import Incomplete
from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google_drive.services.base import GoogleDriveServiceBase as GoogleDriveServiceBase
from typing import Any, Iterable

class GoogleDriveFileService(GoogleDriveServiceBase):
    """Service class for Google Drive file operations.

    This class provides methods for interacting with the files() endpoint
    of the Google Drive API.
    """
    files_service: Incomplete
    def __init__(self, credentials: GoogleCredentials) -> None:
        """Initialize the Google service with credentials.

        Args:
            credentials (GoogleCredentials): The credentials for the service
        """
    def get_file(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get file metadata.

        Args:
            params: Parameters for the files().get() request

        Returns:
            The file metadata
        """
    def list_files(self, params: dict[str, Any]) -> dict[str, Any]:
        """List files.

        Args:
            params: Parameters for the files().list() request

        Returns:
            List of files and folders
        """
    def list_files_iterate(self, params: dict[str, Any]) -> Iterable[dict[str, Any]]:
        """Iterate multiple list files page from Google Drive file.

        Args:
            params: Parameters for the files().list() request

        Yields:
            Iterable[Dict[str, Any]]: List of files from a Google Drive file
        """
    def create_file(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a file.

        Args:
            params: Parameters for the files().create() request

        Returns:
            The created file's metadata
        """
    def update_file(self, params: dict[str, Any]) -> dict[str, Any]:
        """Update a file.

        Args:
            params: Parameters for the files().update() request

        Returns:
            The updated file's metadata
        """
    def delete_file(self, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a file.

        Args:
            params: Parameters for the files().delete() request

        Returns:
            Empty response upon success
        """
    def copy_file(self, params: dict[str, Any]) -> dict[str, Any]:
        """Copy a file.

        Args:
            params: Parameters for the files().copy() request

        Returns:
            The copied file's metadata
        """
