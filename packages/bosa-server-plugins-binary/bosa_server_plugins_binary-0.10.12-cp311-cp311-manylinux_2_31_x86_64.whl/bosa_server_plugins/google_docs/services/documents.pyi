from _typeshed import Incomplete
from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google_docs.services.base import GoogleDocsServiceBase as GoogleDocsServiceBase
from typing import Any

class GoogleDocsDocumentsService(GoogleDocsServiceBase):
    """Service class for Google Docs document operations.

    This class provides methods for interacting with the documents() endpoint
    of the Google Docs API.
    """
    documents_service: Incomplete
    def __init__(self, credentials: GoogleCredentials) -> None:
        """Initialize the Google service with credentials.

        Args:
            credentials (GoogleCredentials): The credentials for the service
        """
    def create_document(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a document.

        Args:
            params: Parameters for the documents().create() request

        Returns:
            The created document's metadata
        """
    def get_document(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get document metadata and content.

        Args:
            params: Parameters for the documents().get() request

        Returns:
            The document metadata and content
        """
    def batch_update_document(self, params: dict[str, Any]) -> dict[str, Any]:
        """Apply batch updates to a document.

        Args:
            params: Parameters for the documents().batchUpdate() request

        Returns:
            Results of the batch update operation
        """
