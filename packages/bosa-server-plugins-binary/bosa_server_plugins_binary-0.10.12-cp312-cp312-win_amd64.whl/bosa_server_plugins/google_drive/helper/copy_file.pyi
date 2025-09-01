from bosa_server_plugins.google_drive.requests.files import CopyFileRequest as CopyFileRequest
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService

def copy_file(request: CopyFileRequest, service: GoogleDriveFileService):
    """Copy a file in Google Drive.

    Args:
        request: The request object
        service: GoogleDriveFileService instance
    """
