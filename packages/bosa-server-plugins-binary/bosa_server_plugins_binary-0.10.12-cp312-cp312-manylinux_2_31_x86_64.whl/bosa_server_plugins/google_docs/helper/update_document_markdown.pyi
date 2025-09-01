from bosa_server_plugins.google_docs.requests.documents import UpdateDocumentMarkdownRequest as UpdateDocumentMarkdownRequest
from bosa_server_plugins.google_drive.requests.files import UpdateFileRequest as UpdateFileRequest
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService
from bosa_server_plugins.handler import InputFile as InputFile

async def update_document_markdown(request: UpdateDocumentMarkdownRequest, drive_service: GoogleDriveFileService):
    """Update a Google Doc with Markdown content.

    This function serves as a wrapper for the Google Docs API v1 documents().batchUpdate() method.

    Args:
        request: The UpdateDocumentMarkdownRequest object containing update details
        drive_service: The Google Drive service
    Returns:
        The updated document resource
    """
