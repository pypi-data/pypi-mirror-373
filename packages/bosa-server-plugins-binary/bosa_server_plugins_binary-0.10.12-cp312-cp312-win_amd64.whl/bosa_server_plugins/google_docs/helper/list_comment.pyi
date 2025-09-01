from bosa_server_plugins.google_docs.requests.comments import ListCommentsRequest as ListCommentsRequest
from bosa_server_plugins.google_drive.services.comments import GoogleDriveCommentsService as GoogleDriveCommentsService

def list_comment(request: ListCommentsRequest, service: GoogleDriveCommentsService):
    """List comments in a Google Doc.

    This function serves as a wrapper for the Google Drive API v3 comments().list() method.

    Args:
        request: The ListCommentsRequest object containing request details
        service: The Google Drive comments service

    Returns:
        The list of comments include replies of that comment in a document
    """
