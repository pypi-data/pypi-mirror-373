from _typeshed import Incomplete
from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google_drive.services.base import GoogleDriveServiceBase as GoogleDriveServiceBase
from typing import Any, Iterable

class GoogleDriveCommentsService(GoogleDriveServiceBase):
    """Service class for Google Drive comments and replies operations.

    This class provides methods for managing comments and replies on Google Drive files.
    """
    comments_service: Incomplete
    replies_service: Incomplete
    def __init__(self, credentials: GoogleCredentials) -> None:
        """Initialize the Google service with credentials.

        Args:
            credentials (GoogleCredentials): The credentials for the service
        """
    def list_comments(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get comments from Google Drive file.

        Args:
            params: Parameters for the comments().list() request

        Returns:
            List of comments from a Google Drive file
        """
    def list_comments_iterate(self, params: dict[str, Any]) -> Iterable[dict[str, Any]]:
        """Iterate multiple comments page from Google Drive file.

        Args:
            params: Parameters for the comments().list() request

        Yields:
            Iterable[Dict[str, Any]]: List of comments from a Google Drive file
        """
    def list_replies(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get replies from Google Drive comment.

        Args:
            params: Parameters for the replies().list() request

        Returns:
            List of replies from a Google Drive comment
        """
