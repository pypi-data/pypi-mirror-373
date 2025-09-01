from _typeshed import Incomplete
from bosa_server_plugins.google_drive.requests.download import DownloadFileRequest as DownloadFileRequest
from bosa_server_plugins.google_drive.services.download import GoogleDriveDownloadService as GoogleDriveDownloadService
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService

GOOGLE_WORKSPACE_FILE_MIMETYPE_EXTENSION: Incomplete
EXPORT_EXTENSION_MIMETYPE: Incomplete

def download_file(request: DownloadFileRequest, file_service: GoogleDriveFileService, download_service: GoogleDriveDownloadService) -> dict:
    """Download a file from Google Drive, handling both regular files and Google Workspace files.

    Args:
        request: The request object.
        file_service: GoogleDriveFileService instance.
        download_service: GoogleDriveDownloadService instance.

    Returns:
        Dict containing the file content, size, filename, and mimetype.
    """
