from bosa_server_plugins.common.mimetypes import MimeTypes as MimeTypes
from bosa_server_plugins.google_docs.requests.documents import GetListDocumentsRequest as GetListDocumentsRequest
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService

def list_documents(request: GetListDocumentsRequest, service: GoogleDriveFileService):
    """List Google Docs in Google Drive.

    This function serves as a wrapper for the Google Drive API v3 files().list() method,
    filtering for only Google Docs type files.

    Args:
        request: The GetListDocumentsRequest object containing request parameters
        service: The Google Drive service

    Returns:
        Dictionary containing the list of documents and next page token if available
    """
