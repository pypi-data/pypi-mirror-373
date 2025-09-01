from bosa_server_plugins.google.services.user_info import GoogleUserInfoService as GoogleUserInfoService
from bosa_server_plugins.google_docs.common.mimetype import GOOGLE_DOCS_SUPPORTED_MIME_TYPES as GOOGLE_DOCS_SUPPORTED_MIME_TYPES
from bosa_server_plugins.google_docs.requests.comments import SummarizeCommentsRequest as SummarizeCommentsRequest
from bosa_server_plugins.google_drive.services.comments import GoogleDriveCommentsService as GoogleDriveCommentsService
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService

def summarize_comment(request: SummarizeCommentsRequest, comment_service: GoogleDriveCommentsService, file_service: GoogleDriveFileService, user_info_service: GoogleUserInfoService):
    """Summarize comments in a Google Doc.

    Args:
        request: The SummarizeCommentsRequest object containing request details
        comment_service: The Google Drive comments service
        file_service: The Google Drive file service
        user_info_service: The Google User Info service

    Returns:
        The summary of comments in the document
    """
