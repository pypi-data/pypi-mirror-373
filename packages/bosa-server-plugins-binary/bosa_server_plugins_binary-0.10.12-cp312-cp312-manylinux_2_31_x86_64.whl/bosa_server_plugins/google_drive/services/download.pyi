from _typeshed import Incomplete
from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google_drive.services.base import GoogleDriveServiceBase as GoogleDriveServiceBase
from typing import Any

class GoogleDriveDownloadService(GoogleDriveServiceBase):
    """Service class for Google Drive download operations.

    This class provides methods for downloading content from Google Drive
    using various endpoints of the Google Drive API.
    """
    files_service: Incomplete
    revisions_service: Incomplete
    def __init__(self, credentials: GoogleCredentials) -> None:
        """Initialize the Google service with credentials.

        Args:
            credentials (GoogleCredentials): The credentials for the service
        """
    def export_file(self, params: dict[str, Any]) -> bytes:
        """Export a Google Workspace document.

        Args:
            params: Parameters for the files().export() request

        Returns:
            The exported file content
        """
    def get_revision_media(self, params: dict[str, Any]) -> bytes:
        """Get revision media content.

        Args:
            params: Parameters for the revisions().get_media() request

        Returns:
            The revision's media content
        """
    def get_file_media(self, params: dict[str, Any]) -> bytes:
        """Get file media content.

        Args:
            params: Parameters for the files().get_media() request

        Returns:
            The file's media content
        """
