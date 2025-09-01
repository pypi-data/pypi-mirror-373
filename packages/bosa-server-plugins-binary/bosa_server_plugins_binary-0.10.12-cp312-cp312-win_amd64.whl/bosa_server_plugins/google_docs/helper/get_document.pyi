from bosa_server_plugins.google_docs.requests.documents import GetDocumentRequest as GetDocumentRequest
from bosa_server_plugins.google_docs.services.documents import GoogleDocsDocumentsService as GoogleDocsDocumentsService

def get_document(request: GetDocumentRequest, service: GoogleDocsDocumentsService):
    """Get a Google Doc by ID.

    This function serves as a wrapper for the Google Docs API v1 documents().get() method.

    Args:
        request: The GetDocumentRequest object
        service: The Google Docs service

    Returns:
        The requested document resource
    """
