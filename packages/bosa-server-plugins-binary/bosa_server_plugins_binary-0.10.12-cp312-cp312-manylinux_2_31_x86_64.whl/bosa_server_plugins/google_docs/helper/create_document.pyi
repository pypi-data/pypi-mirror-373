from bosa_server_plugins.google_docs.requests.documents import CreateDocumentRequest as CreateDocumentRequest
from bosa_server_plugins.google_docs.services.documents import GoogleDocsDocumentsService as GoogleDocsDocumentsService
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService

ROOT_FOLDER_ID: str

def create_document(request: CreateDocumentRequest, documents_service: GoogleDocsDocumentsService, file_service: GoogleDriveFileService):
    """Create a new Google Doc.

    This function serves as a wrapper for the Google Docs API v1 documents().create() method.

    Args:
        request: The CreateDocumentRequest object containing document details
        documents_service: The Google Docs documents service
        file_service: The Google Drive file service

    Returns:
        The created document resource
    """
