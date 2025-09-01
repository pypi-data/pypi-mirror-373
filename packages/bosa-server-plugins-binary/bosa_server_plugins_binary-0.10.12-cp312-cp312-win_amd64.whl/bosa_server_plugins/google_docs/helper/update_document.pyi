from bosa_server_plugins.google_docs.requests.documents import BatchUpdateDocumentRequest as BatchUpdateDocumentRequest
from bosa_server_plugins.google_docs.services.documents import GoogleDocsDocumentsService as GoogleDocsDocumentsService

def update_document(request: BatchUpdateDocumentRequest, service: GoogleDocsDocumentsService):
    """Batch update a Google Doc.

    This function serves as a wrapper for the Google Docs API v1 documents().batchUpdate() method.

    Args:
        request: The BatchUpdateDocumentRequest object containing update details
        service: The Google Docs service

    Returns:
        The updated document resource
    """
